print()
print('⚙️ Lancement génération des Html')
print()

import os
import json
import platform
import locale
import time
from jinja2 import Environment, FileSystemLoader
from display_enrichies import enrichir_valeurs
from export_dashboards import normalize_slug
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
                if any(k.startswith("1_") or k.startswith("2_") or k.startswith("3_") for k in valeurs):
                    triplets.append((valeurs, meta, tmp_meta))
            except Exception as e:
                print(f"⛔ Erreur lecture JSON dans {tmp_valeurs} : {e}")

    if not triplets:
        print(f"❌ Aucun sous-dossier avec fichiers JSON complets dans : {periode_dir}")
    return triplets

# === Générer le rapport HTML pour un contrat donné ===
def generate_report(client_dir, periode):
    print("")
    print(f"\n🔧 Génération du rapport pour {client_dir} ({periode})")
    short_periode = periode[2:]
    triplets = charger_contrat_data(client_dir, periode)
    if not triplets:
        print(f"⚠️ Données absentes ou incomplètes pour {client_dir}")
        return False

    # 1. Enrichissement
    t0 = time.time()
    contexte = {}
    for valeurs, meta, meta_path in triplets:
        dashboard_name = meta.get("dashboard", "default")
        print(f"DEBUG dashboard name: {dashboard_name}")

        partial_ctx = enrichir_valeurs(valeurs, meta_path, client_dir, short_periode)

        # Ajout contrôlé des clés sans écrasement des précédentes
        for k, v in partial_ctx.items():
            if k not in contexte:
                contexte[k] = v
            else:
                if "year" in k.lower():
                    contexte[k] = v

        # print(f"DEBUG clés enrichies : {list(partial_ctx.keys())}")

    print(f"⏱️ enrichir_valeurs : {round(time.time() - t0, 2)}s")
    contexte.update(meta)

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

    if platform.system() == "Windows":
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    else:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    mois_str = datetime.strptime(periode, "%Y-%m").strftime("%B %Y").capitalize()
    contexte["periode_client"] = mois_str

    dashboard_slug = normalize_slug(meta.get("dashboard", ""))
    contexte["dashboard_slug"] = dashboard_slug
    contexte["images_dir"] = f"../../../exports/{client_dir}/{short_periode}/{dashboard_slug}"

    templates = ["1_template_presentation.html", "2_template_client_machine.html", "3_template_index.html"]
    rendered_parts = []

    for tpl_name in templates:
        try:
            start_tpl = time.time()
            tpl_path = f"{client_dir}/{tpl_name}"
            tpl = env.get_template(tpl_path)
            rendered_parts.append(tpl.render(**contexte))
            print(f"⏱️ Rendu {tpl_name} : {round(time.time() - start_tpl, 2)}s")
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

    print(contexte.keys())
    print(f"✅ Rapport HTML généré : {out_path}")
    print("")
    return True

# === Générer tous les rapports d'un mois donné ===
def generate_all_reports(periode):
    contrats_dir = os.path.join(DATA_DIR)
    print("")
    print(f"📂 Lecture du répertoire contrats : {contrats_dir}")

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
    print("")
    print("\n📊 RÉCAPITULATIF")
    print("===========================")
    print(f"🕒 Durée totale d'exécution : {round(duree, 2)} secondes")
    print(f"📁 Total de contrats traités : {total}")
    print(f"✅ Rapports réussis : {total - len(erreurs)}")
    print(f"❌ Échecs : {len(erreurs)}")
    if erreurs:
        print("🔎 Contrats en erreur :", ", ".join(erreurs))

# === Lancement direct depuis le terminal ===
if __name__ == "__main__":
    periode_reference = "2025-05"
    # periode_reference = input("📅 Entrez la période (AAAA-MM) à traiter : ").strip()
    generate_all_reports(periode_reference)
