import os
import json
import platform
import locale
import time
import argparse
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from display_enrichies import enrichir_valeurs
from export_dashboards import normalize_slug
from datetime import datetime
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfReader, PdfWriter

print()
heure_actuelle = datetime.now().strftime("%H:%M:%S")
print(f'⚙️ Lancement génération des Html à {heure_actuelle}')
print()

# === Définition des chemins de base ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "app", "templates")
HTML_BASE_DIR = os.path.join(BASE_DIR, "..", "html")
PDF_BASE_DIR = os.path.join(BASE_DIR, "..", "pdf")
DATA_DIR = os.path.join(BASE_DIR, "..", "exports")
CONFIG_PDF_PATH = os.path.join(BASE_DIR, "..", "config_pdf.xlsx")

# === Analyse des arguments de ligne de commande ===
parser = argparse.ArgumentParser(description="Génère les rapports HTML (et optionnellement les PDF)")
parser.add_argument("--pdf", action="store_true", help="Générer également les PDF")
parser.add_argument("--periode", type=str, default="2025-06", help="Période à traiter (AAAA-MM)")
args = parser.parse_args()

GENERER_PDF = args.pdf
periode_reference = args.periode

# === Chargement du fichier de configuration PDF ===
config_df = pd.read_excel(CONFIG_PDF_PATH)

# === Initialisation de l'environnement Jinja2 ===
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# === Filtres Jinja2 personnalisés ===
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

# === Fonction PDF via Playwright ===
def html_to_pdf_with_playwright(html_path, pdf_output_path):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            url = "file://" + os.path.abspath(html_path).replace("\\", "/")
            page.goto(url)
            page.pdf(path=pdf_output_path, format="A4", print_background=True)
            browser.close()
            print(f"📄 PDF généré (Playwright) : {pdf_output_path}")
    except Exception as e:
        print(f"❌ Erreur PDF Playwright : {e}")

# === Découpe de PDF selon config ===
def decouper_pdf(source_path, output_path, pages_str):
    try:
        reader = PdfReader(source_path)
        writer = PdfWriter()
        pages = []
        for part in pages_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.extend(range(start - 1, end))
            else:
                pages.append(int(part) - 1)
        for i in pages:
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"📄 PDF partiel généré : {output_path}")
    except Exception as e:
        print(f"❌ Erreur découpe PDF : {e}")

# === Charger les données JSON (valeurs + meta) ===
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
    if not triplets:
        print(f"❌ Aucun sous-dossier avec fichiers JSON complets dans : {periode_dir}")
    return triplets

# === Générer le rapport HTML et PDF pour un contrat donné ===
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
            if k not in contexte or "year" in k.lower():
                contexte[k] = v

    contexte["valeurs_multi"] = valeurs_multi
    contexte["name_client"] = client_dir

    if platform.system() == "Windows":
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    else:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    mois_str = datetime.strptime(periode, "%Y-%m").strftime("%B %Y").capitalize()
    contexte["periode_client"] = mois_str

    templates = ["1_template_presentation.html", "2_template_client_machine.html", "3_template_index.html"]
    rendered_parts = []
    for tpl_name in templates:
        try:
            tpl_path = f"{client_dir}/{tpl_name}"
            tpl = env.get_template(tpl_path)
            rendered_parts.append(tpl.render(**contexte))
        except Exception as e:
            print(f"❌ Erreur avec le template {tpl_name} pour {client_dir}: {e}")
            return False

    final_html = "\n".join(rendered_parts)
    dossier_output = os.path.join(HTML_BASE_DIR, client_dir, short_periode)
    os.makedirs(dossier_output, exist_ok=True)
    out_name = f"{client_dir}_{short_periode}.html".replace(" ", "_").replace("-", "_")
    out_path = os.path.join(dossier_output, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ Rapport HTML généré : {out_path}\n")

    if not GENERER_PDF:
        return True

    # === Génération du PDF complet ===
    dossier_pdf = os.path.join(PDF_BASE_DIR, client_dir, short_periode)
    os.makedirs(dossier_pdf, exist_ok=True)

    row = config_df[(config_df['Contrat'] == client_dir) & (config_df['Période'] == periode)]
    if row.empty:
        print(f"⚠️ Aucun paramétrage PDF trouvé pour {client_dir} ({periode})")
        return True

    nom_pdf_complet = row.iloc[0]['Nom_PDF_Complet'].replace('"Contrat"', client_dir).replace('"Période"', short_periode)
    nom_pdf_partiel = row.iloc[0]['Nom_PDF_Partiel'].replace('"Contrat"', client_dir).replace('"Période"', short_periode)
    pages_partiel = row.iloc[0]['Pages_Partiel']

    path_pdf_complet = os.path.join(dossier_pdf, nom_pdf_complet + ".pdf")
    path_pdf_partiel = os.path.join(dossier_pdf, nom_pdf_partiel + ".pdf")

    html_to_pdf_with_playwright(out_path, path_pdf_complet)
    decouper_pdf(path_pdf_complet, path_pdf_partiel, pages_partiel)

    return True

# === Générer tous les rapports pour une période donnée ===
def generate_all_reports(periode):
    contrats_dir = os.path.join(DATA_DIR)
    print(f"\n📂 Lecture du répertoire contrats : {contrats_dir}")
    start_time = time.time()
    total = 0
    erreurs = []
    for contrat_id in os.listdir(contrats_dir):
        chemin_complet = os.path.join(contrats_dir, contrat_id)
        if os.path.isdir(chemin_complet):
            success = generate_report(contrat_id, periode)
            total += 1
            if not success:
                erreurs.append(contrat_id)
        else:
            print(f"⏭️ Ignoré (pas un dossier): {contrat_id}")
    duree = time.time() - start_time
    print("\n\n📊 RÉCAPITULATIF")
    print("===========================")
    print(f"🕒 Durée totale d'exécution : {round(duree, 2)} secondes")
    print(f"📁 Total de contrats traités : {total}")
    print(f"✅ Rapports réussis : {total - len(erreurs)}")
    print(f"❌ Échecs : {len(erreurs)}")
    if erreurs:
        print("🔎 Contrats en erreur :", ", ".join(erreurs))

# === Lancement ===
generate_all_reports(periode_reference)
