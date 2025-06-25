import os
import json
import platform
import locale
from jinja2 import Environment, FileSystemLoader
from display_enrichies import enrichir_valeurs
from datetime import datetime

# === Définition du chemin de base ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "app", "templates")
HTML_BASE_DIR = os.path.join(BASE_DIR, "..", "html")
DATA_DIR = os.path.join(BASE_DIR, "..", "exports")

# === Initialisation de l'environnement Jinja2 ===
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# === Charger les données JSON (valeurs + meta) pour un contrat ===
def charger_contrat_data(client_dir, periode):
    short_periode = periode[2:]  # Convertit '2025-05' en '25-05'
    periode_dir = os.path.join(DATA_DIR, client_dir, short_periode)

    if not os.path.isdir(periode_dir):
        print(f"❌ Période non trouvée : {periode_dir}")
        return None, None

    sous_dossiers = [d for d in os.listdir(periode_dir) if os.path.isdir(os.path.join(periode_dir, d))]
    if not sous_dossiers:
        print(f"❌ Aucun sous-dossier de contrat trouvé dans : {periode_dir}")
        return None, None

    contrat_path = None
    valeurs_path = None
    meta_path = None

    for dossier in sous_dossiers:
        tmp_path = os.path.join(periode_dir, dossier)
        tmp_valeurs = os.path.join(tmp_path, "valeurs.json")
        tmp_meta = os.path.join(tmp_path, "meta.json")
        if os.path.exists(tmp_valeurs) and os.path.exists(tmp_meta):
            try:
                with open(tmp_valeurs, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Vérifie la présence d'au moins une clé "1_", "2_", ou "3_"
                if any(k.startswith("1_") or k.startswith("2_") or k.startswith("3_") for k in data):
                    contrat_path = tmp_path
                    valeurs_path = tmp_valeurs
                    meta_path = tmp_meta
                    break
            except Exception as e:
                print(f"⛔ Erreur lecture JSON dans {tmp_valeurs} : {e}")

    if not contrat_path:
        print(f"❌ Aucun sous-dossier avec fichiers JSON complets et pertinents dans : {periode_dir}")
        return None, None

    with open(valeurs_path, "r", encoding="utf-8") as f:
        valeurs = json.load(f)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return valeurs, meta

# === Générer le rapport HTML pour un contrat donné ===
def generate_report(client_dir, periode):
    print(f"\n🔧 Génération du rapport pour {client_dir} ({periode})")
    valeurs, meta = charger_contrat_data(client_dir, periode)
    if not valeurs or not meta:
        print(f"⚠️  Données absentes ou incomplètes pour {client_dir}")
        return

    contexte = enrichir_valeurs(valeurs)
    contexte.update(meta)

    # Table d'alias de noms à afficher
    alias_clients = {
        "Alvend_Conditionnement": "Conditionnement",
        "Alvend_Stockage": "Stockage",
        "ITM_Doullens": "ITM Doullens",
        "ITM_Gouvieux": "ITM Gouvieux",
        "ITM_Lambersart": "ITM Lambersart",
        "ITM_Le_Quesnoy": "ITM Le Quesnoy",
        "ITM_Montigny": "ITM Montigny",
        "ITM_PAM": "ITM Pont-à-Marcq",
        "Quercy_Cholet2": "Quercy Cholet2",
        "Quercy_Guilmot": "Quercy Guilmot Gaudais",
    }

    contexte["name_client"] = client_dir
    contexte["nom_affiche_client"] = alias_clients.get(client_dir, client_dir)

    # Choix de la locale pour afficher les mois en français
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
            return

    final_html = "\n".join(rendered_parts)
    short_periode = periode[2:]  # '2025-05' -> '25-05'
    dossier_output = os.path.join(HTML_BASE_DIR, client_dir, short_periode)
    os.makedirs(dossier_output, exist_ok=True)

    out_name = f"{client_dir}_{short_periode}.html".replace(" ", "_").replace("-", "_")
    out_path = os.path.join(dossier_output, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ Rapport HTML généré : {out_path}")

# === Générer tous les rapports d'un mois donné ===
def generate_all_reports(periode):
    contrats_dir = os.path.join(DATA_DIR)
    print(f"📂 Lecture du répertoire contrats : {contrats_dir}")

    for contrat_id in os.listdir(contrats_dir):
        chemin_complet = os.path.join(contrats_dir, contrat_id)
        if os.path.isdir(chemin_complet):
            generate_report(contrat_id, periode)
        else:
            print(f"⏭️  Ignoré (pas un dossier): {contrat_id}")

# === Lancement direct depuis le terminal ===
if __name__ == "__main__":
    periode_reference = "2025-05"
    # periode_reference = input("📅 Entrez la période (AAAA-MM) à traiter : ").strip()
    generate_all_reports(periode_reference)
