import os
import json
import re
import unicodedata
import time
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# === CHARGEMENT VARIABLES ENV ===
script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

username = os.getenv("GRAFANA_USER")
password = os.getenv("GRAFANA_PASS")
grafana_base = "https://view.preprod.fitt-solutions.fr"

# === CHARGEMENT DU FICHIER CONTRATS ===
excel_path = os.path.join(project_root, "data", "Contrats_FiTT.xlsx")
df = pd.read_excel(excel_path)
df.ffill(inplace=True)

# === DÉTECTION PÉRIODE RÉFÉRENCE ===
def get_previous_month_range():
    today = datetime.today().replace(day=1)
    last_month = today - timedelta(days=1)
    start = last_month.replace(day=1)
    end = last_month.replace(day=last_month.day)
    return start, end

# === NORMALISATION DU SLUG ===
def normalize_slug(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return text

# === EXPORTATION DASHBOARD ===
def export_dashboard(contrat, uid, slug, panel_ids, panel_types, from_str, to_str, periode_reference):
    export_dir = os.path.join(project_root, "exports", contrat, periode_reference, normalize_slug(slug))
    os.makedirs(export_dir, exist_ok=True)

    print(f"\n🚧 DÉBUT EXPORT : {contrat} / {slug}")
    print(f"   🔍 UID = {uid}")
    print(f"   🗓️  Période = {from_str} → {to_str}")
    print(f"   🎯 Panels ciblés : {panel_ids}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 4000})
        page = context.new_page()

        print("🔐 Connexion à Grafana...")
        page.goto(f"{grafana_base}/login")
        page.fill('input[name="user"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)

        print("🧼 Nettoyage état précédent (about:blank)...")
        page.goto("about:blank")
        page.wait_for_timeout(1000)

        url = f"{grafana_base}/d/{uid}/{slug}?orgId=1&from={from_str}&to={to_str}"
        print(f"➡️ Chargement du dashboard : {url}")
        page.goto(url)
        page.wait_for_timeout(45000)

        current_url = page.url
        expected_slug = normalize_slug(slug)
        if expected_slug not in current_url:
            print(f"❌ Mismatch dashboard : attendu '{expected_slug}', mais trouvé : '{current_url}'")
            return

        page.reload()
        page.wait_for_timeout(15000)

        all_panels = page.locator("div.panel-container, div.react-grid-item")
        total = all_panels.count()
        print(f"🔎 Panels détectés : {total}")

        values = {}
        images = []

        for pid, ptype in zip(panel_ids, panel_types):
            print(f"   ▶️ Panel #{pid} ({ptype})...")

            if pid >= total:
                print(f"   ⚠️ Panel #{pid} hors limite ({total} max)")
                continue

            panel = all_panels.nth(pid)

            if ptype == "graph":
                panel.evaluate("""
                    (el) => {
                        const header = el.querySelector('[data-testid="header-container"]');
                        if (header) header.style.display = 'none';
                    }
                """)
                path = os.path.join(export_dir, f"graph_{pid}.png")

                box = panel.bounding_box()
                if box:
                    panel.screenshot(
                        path=path,
                        clip={
                            "x": box["x"]+1,
                            "y": box["y"]+1,
                            "width": box["width"]-1,
                            "height": box["height"] - 26  # ⬅️ on rogne le bas
                        }
                    )
                    images.append(f"graph_{pid}.png")
                    print(f"   📸 Graphique capturé : graph_{pid}.png (marge basse supprimée)")
                else:
                    print(f"❌ Impossible de récupérer les dimensions du panel {pid}")



            elif ptype == "stat":
                raw = panel.text_content().strip()
                match = re.search(r"(.*?)([\-]?\d+[.,]?\d*)\s?(?:kWh|MWh|%|€|kW)?", raw)
                if match:
                    label = match.group(1).strip() or f"valeur_{pid}"
                    val = match.group(2).strip()
                    key = f"{pid}_{label.replace(' ', '_')}"
                    values[key] = val
                    print(f"   🔢 Valeur extraite (sans unité) : {key} = {val}")
                else:
                    print(f"   ❌ Aucune valeur détectée dans panel #{pid}")

        with open(os.path.join(export_dir, "valeurs.json"), "w", encoding="utf-8") as f:
            json.dump(values, f, indent=2, ensure_ascii=False)

        with open(os.path.join(export_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({
                "dashboard": slug,
                "from": from_str,
                "to": to_str,
                "captured_graphs": images,
                "captured_values": list(values.keys())
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Export terminé pour {contrat} / {slug}")
        browser.close()

# === TRAITEMENT MULTI-CONTRATS ===
def main():
    print("\n🚀 Lancement de l'export automatique multi-contrats...")
    start = time.time()

    mois_precedent = get_previous_month_range()
    periode_reference_full = mois_precedent[1].strftime("%Y-%m")
    periode_reference_short = mois_precedent[1].strftime("%y-%m")
    date_fin_mois_precedent = mois_precedent[1].strftime("%Y-%m-%dT23:59:59Z")

    groups = df.groupby(["Contrat", "UID Dashboard", "Nom du Dashboard"])

    total = 0
    erreurs = []

    for (contrat, uid, slug), group in groups:
        panel_ids = group["ID Panel à extraire"].tolist()
        panel_types = group["Nature du panel"].tolist()
        date_debut = group["Date Début"].iloc[0]

        if isinstance(date_debut, str) and "enregistré" in date_debut.lower():
            from_str = mois_precedent[0].strftime("%Y-%m-%dT00:00:00Z")
            to_str = mois_precedent[1].strftime("%Y-%m-%dT23:59:59Z")
        else:
            from_str = pd.to_datetime(date_debut).strftime("%Y-%m-%dT00:00:00Z")
            to_str = date_fin_mois_precedent

        try:
            export_dashboard(contrat, uid, slug, panel_ids, panel_types, from_str, to_str, periode_reference_short)
            total += 1
        except Exception as e:
            erreurs.append(f"{contrat} / {slug}")
            print(f"❌ Erreur export pour {contrat} / {slug} : {e}")

    duree_sec = round(time.time() - start, 2)
    minutes = int(duree_sec // 60)
    secondes = int(duree_sec % 60)
    print("\n📊 RÉCAPITULATIF EXPORT")
    print("===========================")
    print(f"🕒 Durée totale d'exécution : {minutes} min {secondes} sec")
    print(f"📁 Contrats exportés : {total}")
    print(f"❌ Échecs détectés : {len(erreurs)}")
    if erreurs:
        print("🔎 Contrats en erreur :", ", ".join(erreurs))

# === LANCEMENT ===
if __name__ == "__main__":
    main()
