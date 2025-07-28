import os
import json
import platform
import locale
import time
import argparse
import pandas as pd
import re
import csv
from jinja2 import Environment, FileSystemLoader, Template
from display_enrichies import enrichir_valeurs
from export_dashboards import normalize_slug
from alias_resolver import image_aliases
from datetime import datetime
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfReader, PdfWriter
import tempfile

# === Définition des chemins de base ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "app", "templates")
HTML_BASE_DIR = os.path.join(BASE_DIR, "..", "html")
PDF_BASE_DIR = os.path.join(BASE_DIR, "..", "pdf")
DATA_DIR = os.path.join(BASE_DIR, "..", "exports")
SYNTH_DIR = os.path.join(BASE_DIR, "..", "synthese")
CONFIG_PDF_PATH = os.path.join(BASE_DIR, "..", "data", "config_pdf.xlsx")
CONTRATS_FITT_PATH = os.path.join(BASE_DIR, "..", "data", "Contrats_FiTT.xlsx")
contrats_fitt_df = pd.read_excel(CONTRATS_FITT_PATH)

# === Analyse des arguments de ligne de commande ===
parser = argparse.ArgumentParser(description="Génère les rapports HTML (et optionnellement les PDF)")
parser.add_argument("--pdf", action="store_true", help="Générer également les PDF")
parser.add_argument("--periode", type=str, default="2025-06", help="Période à traiter (AAAA-MM)")
parser.add_argument("--contrat", action="append", help="Contrat(s) à traiter (répétable)", default=[])
args = parser.parse_args()

GENERER_PDF = args.pdf
periode_reference = args.periode

# === Chargement du fichier de configuration PDF ===
config_df = pd.read_excel(CONFIG_PDF_PATH)

# === Initialisation de l'environnement Jinja2 ===
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def format_virgule(valeur):
    try:
        return str(valeur).replace('.', ',')
    except Exception:
        return valeur

def format_virgule_1(valeur):
    try:
        nombre = float(valeur)
        return f"{nombre:.1f}".replace('.', ',')
    except (ValueError, TypeError):
        return valeur

env.filters['virgule'] = format_virgule
env.filters['virgule1'] = format_virgule_1

# === Génération PDF de synthèse globale ===
def generer_pdf_synthese(periode, synthese_contrats):
    html_synthese = """
    <html><head>
    <meta charset='utf-8'>
    <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    h1 { color: #003366; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
    th { background-color: #003366; color: white; }
    .ok { color: green; font-weight: bold; }
    .warn { color: orange; font-weight: bold; }
    .fail { color: red; font-weight: bold; }
    </style>
    </head><body>
    <h1>Synthèse des rapports - {{ periode }}</h1>
    <table>
    <tr>
        <th>Contrat</th>
        <th>PDF Complet</th>
        <th>PDF Partiel</th>
        <th>Début CPE</th>
        <th>Données</th>
    </tr>
    {% for ligne in donnees %}
    <tr>
        <td>{{ ligne.contrat }}</td>
        <td class="{{ ligne.etat_pdf }}">{{ ligne.pdf_complet }}</td>
        <td class="{{ ligne.etat_partiel }}">{{ ligne.pdf_partiel }}</td>
        <td>{{ ligne.date_debut }}</td>
        <td class="{{ ligne.etat_data }}">{{ ligne.alertes }}</td>
    </tr>
    {% endfor %}
    </table>
    </body></html>
    """
    t = Template(html_synthese)
    rendu = t.render(periode=periode, donnees=synthese_contrats)
    os.makedirs(os.path.join(PDF_BASE_DIR, "synthese"), exist_ok=True)
    tmp_html_path = os.path.join(tempfile.gettempdir(), "synthese_temp.html")
    with open(tmp_html_path, "w", encoding="utf-8") as f:
        f.write(rendu)
    output_pdf = os.path.join(PDF_BASE_DIR, "synthese", f"synthese_{periode}.pdf")
    html_to_pdf_with_playwright(tmp_html_path, output_pdf)
    print(f"📝 Synthèse PDF générée : {output_pdf}")

def html_to_pdf_with_playwright(html_path, pdf_output_path):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            url = "file://" + os.path.abspath(html_path).replace("\\", "/")
            page.goto(url)
            page.pdf(path=pdf_output_path, format="A4", print_background=True)
            browser.close()
            return True
    except Exception as e:
        print(f"❌ Erreur PDF Playwright : {e}")
        return False

def decouper_pdf(source_path, output_path, pages_str):
    try:
        reader = PdfReader(source_path)
        writer = PdfWriter()
        pages = []

        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = [int(x.strip()) for x in part.split('-')]
                pages.extend(range(start - 1, end))  # end inclus
            else:
                pages.append(int(part) - 1)

        pages = sorted(set(pages))

        print(f"📄 Nombre total de pages dans le PDF complet : {len(reader.pages)}")
        print(f"📑 Pages demandées : {[p+1 for p in pages]}")

        for i in pages:
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
            else:
                print(f"\033[91m⚠️ Page {i+1} ignorée (le PDF n'en contient que {len(reader.pages)})\033[0m")

        with open(output_path, "wb") as f:
            writer.write(f)

        return True

    except Exception as e:
        print(f"❌ Erreur découpe PDF : {e}")
        return False

def charger_contrat_data(client_dir, periode):
    short_periode = periode[2:]
    periode_dir = os.path.join(DATA_DIR, client_dir, short_periode)

    if not os.path.isdir(periode_dir):
        print(f"❌ Période non trouvée : {periode_dir}")
        return []

    sous_dossiers = [d for d in os.listdir(periode_dir) if os.path.isdir(os.path.join(periode_dir, d))]
    if not sous_dossiers:
        print(f"❌ Aucun sous-dossier trouvé dans : {periode_dir}")
        return []

    def priorite_dashboard(nom):
        nom_lower = nom.lower()
        if "mensuel" in nom_lower:
            return 1
        elif "annuel" in nom_lower:
            return 2
        else:
            return 3

    sous_dossiers = sorted(sous_dossiers, key=priorite_dashboard)

    triplets = []
    for dossier in sous_dossiers:
        tmp_path = os.path.join(periode_dir, dossier)
        tmp_valeurs = os.path.join(tmp_path, "valeurs.json")
        tmp_meta = os.path.join(tmp_path, "meta.json")
        if os.path.exists(tmp_valeurs) and os.path.exists(tmp_meta):
            try:
                with open(tmp_valeurs, "r", encoding="utf-8") as f:
                    valeurs = json.load(f)
                with open(tmp_meta, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                triplets.append((valeurs, meta, tmp_meta, dossier))
            except Exception as e:
                print(f"⛔ Erreur lecture JSON dans {tmp_valeurs} : {e}")

    return triplets

# === Fonction de récupération avec fallback et journalisation ===
def get_valeur_safe(contexte, cle, alertes, contrat, default="Abs"):
    if cle in contexte:
        val = contexte[cle]
        if val not in [None, ""]:
            return val
    alertes.append({"contrat": contrat, "cle": cle, "valeur": default})
    return default

def generate_report(client_dir, periode):
    print(f"\n🔧 Génération du rapport pour {client_dir} ({periode})")
    short_periode = periode[2:]
    triplets = charger_contrat_data(client_dir, periode)
    if not triplets:
        print(f"⚠️ Données absentes ou incomplètes pour {client_dir}")
        return False

    contexte = {}
    valeurs_multi = {}
    for valeurs, meta, meta_path, dossier in triplets:
        dashboard_slug = normalize_slug(meta.get("dashboard", dossier))
        alias_slug = dashboard_slug
        valeurs_multi[alias_slug] = {"valeurs": valeurs, "meta": meta, "meta_path": meta_path}

        partial_ctx = enrichir_valeurs(valeurs, meta_path, client_dir, short_periode)

        for k, v in partial_ctx.items():
            if k not in contexte:
                contexte[k] = v
            elif "year" in k.lower() and "annuel" in dashboard_slug:
                contexte[k] = v

    contexte["valeurs_multi"] = valeurs_multi
    contexte["client_dir"] = client_dir
    contexte["name_client"] = client_dir
    contexte["nom_affiche_client"] = image_aliases.get(client_dir, client_dir)

    # === Initialisation des alertes et fonction de fallback pour les templates ===
    alertes = []
    contexte["valeurs"] = lambda key: get_valeur_safe(contexte, key, alertes, client_dir)

    # === Récupération de la date de début CPE depuis Contrats_FiTT.xlsx ===
    try:
        contrat_rows = contrats_fitt_df[contrats_fitt_df['Contrat'].str.lower() == client_dir.lower()]

        for _, row in contrat_rows.iterrows():
            nom_dashboard = str(row.get('Nom du Dashboard', ''))
            if "cpe_annuel" not in nom_dashboard.lower():
                continue

            date_debut_raw = row.get("Date Début", None)

            if isinstance(date_debut_raw, (pd.Timestamp, datetime)):
                date_obj = pd.to_datetime(date_debut_raw)
            elif isinstance(date_debut_raw, str) and re.match(r"\d{4}-\d{2}-\d{2}", date_debut_raw):
                date_obj = pd.to_datetime(date_debut_raw)
            else:
                continue

            try:
                locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            except:
                locale.setlocale(locale.LC_TIME, 'French_France.1252')

            contexte["date_debut_cpe_annuel"] = date_obj.strftime("%B %Y").capitalize()
            break
    except Exception as e:
        print(f"⚠️ Erreur date_debut_cpe_annuel pour {client_dir} : {e}")

    if platform.system() == "Windows":
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    else:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    mois_str = datetime.strptime(periode, "%Y-%m").strftime("%B %Y").capitalize()
    contexte["periode_client"] = mois_str

    try:
        print(f"🧪 Date début CPE Annuel pour {client_dir} : {contexte.get('date_debut_cpe_annuel')}")
        tpl = env.get_template("template_global.html")
        final_html = tpl.render(**contexte)
    except Exception as e:
        print(f"❌ Erreur avec le template global pour {client_dir}: {e}")
        return False

    dossier_output = os.path.join(HTML_BASE_DIR, client_dir, short_periode)
    os.makedirs(dossier_output, exist_ok=True)
    out_name = f"{client_dir}_{short_periode}.html".replace(" ", "_").replace("-", "_")
    out_path = os.path.join(dossier_output, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ HTML : {out_path}")

    # === Écriture du fichier de synthèse des valeurs absentes ===
    if alertes:
        os.makedirs(SYNTH_DIR, exist_ok=True)
        synth_path = os.path.join(SYNTH_DIR, f"synthese_alertes_{periode}.csv")
        with open(synth_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["contrat", "cle", "valeur"])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(alertes)

    if not GENERER_PDF:
        print(f"📄 PDF (non généré - option désactivée)")
        return {
            "success": True,
            "date_debut": contexte.get("date_debut_cpe_annuel", "-")
        }

    dossier_pdf = os.path.join(PDF_BASE_DIR, client_dir, short_periode)
    os.makedirs(dossier_pdf, exist_ok=True)

    config_df['Contrat'] = config_df['Contrat'].astype(str).str.strip()
    config_df['Période'] = config_df['Période'].astype(str).str.strip()

    contrat_nettoye = client_dir.strip().lower()
    periode_nettoyee = periode.strip()

    row = config_df[
        (config_df['Contrat'].str.lower() == contrat_nettoye) &
        (config_df['Période'] == periode_nettoyee)
    ]

    if row.empty:
        row = config_df[
            (config_df['Contrat'].str.lower() == contrat_nettoye) &
            (config_df['Période'].str.upper() == "YYYY-MM")
        ]

    if row.empty:
        print(f"⚠️ PDF : aucun paramétrage trouvé dans config_pdf.xlsx pour {client_dir} / {periode}")
        return {
            "success": True,
            "date_debut": contexte.get("date_debut_cpe_annuel", "-")
        }

    periode_pdf = short_periode.replace("-", "")
    nom_pdf_complet = f"{client_dir}-{periode_pdf}-FiTT"
    nom_pdf_partiel = f"{client_dir}-{periode_pdf}"
    pages_partiel = row.iloc[0]['Pages_Partiel']

    path_pdf_complet = os.path.join(dossier_pdf, nom_pdf_complet + ".pdf")
    path_pdf_partiel = os.path.join(dossier_pdf, nom_pdf_partiel + ".pdf")

    statut_pdf = "❌"
    statut_partiel = "❌"

    if html_to_pdf_with_playwright(out_path, path_pdf_complet):
        statut_pdf = "✅"
        if decouper_pdf(path_pdf_complet, path_pdf_partiel, pages_partiel):
            statut_partiel = "✅"
        else:
            statut_partiel = "⚠️"
    else:
        statut_pdf = "❌"

    print("📄 Récapitulatif :")
    print(f"   PDF Complet  {statut_pdf}  {nom_pdf_complet}.pdf")
    print(f"   PDF Partiel  {statut_partiel}  {nom_pdf_partiel}.pdf")

    return {
        "success": True,
        "date_debut": contexte.get("date_debut_cpe_annuel", "-")
    }

def generate_all_reports(periode):
    contrats_dir = os.path.join(DATA_DIR)
    print(f"\n📂 Lecture du répertoire contrats : {contrats_dir}")
    start_time = time.time()
    total = 0
    erreurs = []
    synthese_contrats = []
    contrats = args.contrat if args.contrat else os.listdir(contrats_dir)
    for contrat_id in contrats:
        chemin_complet = os.path.join(contrats_dir, contrat_id)
        if os.path.isdir(chemin_complet):
            resultat = generate_report(contrat_id, periode)
            success = resultat["success"]
            date_debut = resultat["date_debut"]
            total += 1

            # Vérification si des alertes existent pour ce contrat
            alertes_path = os.path.join(SYNTH_DIR, f"synthese_alertes_{periode}.csv")
            a_des_alertes = False
            if os.path.exists(alertes_path):
                with open(alertes_path, "r", encoding="utf-8") as f:
                    a_des_alertes = any(contrat_id in line for line in f)

            synthese_contrats.append({
                "contrat": contrat_id,
                "pdf_complet": "✅" if success else "❌",
                "pdf_partiel": "✅" if success else "❌",
                "alertes": "🔴 Alerte !" if a_des_alertes else "🟢 OK",
                "etat_pdf": "ok" if success else "fail",
                "etat_partiel": "ok" if success else "fail",
                "etat_data": "fail" if a_des_alertes else "ok",
                "date_debut": date_debut
            })
            if not success:
                erreurs.append(contrat_id)
        else:
            print(f"⏭️ Ignoré (pas un dossier): {contrat_id}")

    generer_pdf_synthese(periode, synthese_contrats)

    duree = time.time() - start_time
    print("\n\n📊 RÉCAPITULATIF GLOBAL")
    print("==========================")
    print(f"🕒 Durée totale d'exécution : {round(duree, 2)} secondes")
    print(f"📁 Total de contrats traités : {total}")
    print(f"✅ Rapports réussis : {total - len(erreurs)}")
    print(f"❌ Échecs : {len(erreurs)}")
    if erreurs:
        print("🔎 Contrats en erreur :", ", ".join(erreurs))

generate_all_reports(periode_reference)