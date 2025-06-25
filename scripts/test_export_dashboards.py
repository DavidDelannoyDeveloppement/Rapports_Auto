import os
import re
import json
import csv
from datetime import datetime
from urllib.parse import urlencode
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# === CONFIGURATION ===

dashboard_uid = "ee3jazig3cz5se"
dashboard_slug = "itm-gouvieux-1-cpe-mensuel"
grafana_base = "https://view.preprod.fitt-solutions.fr"
org_id = 1

# === CHARGEMENT .env ===

script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

username = os.getenv("GRAFANA_USER")
password = os.getenv("GRAFANA_PASS")

# === DATES À EXPORTER ===

date_debut = datetime(2025, 5, 1)
date_fin = datetime(2025, 5, 31)
from_str = date_debut.strftime("%Y-%m-%dT00:00:00Z")
to_str = date_fin.strftime("%Y-%m-%dT23:59:59Z")

folder_name = date_debut.strftime("%Y-%m")
export_dir = os.path.join(project_root, "exports", "itm-gouvieux", folder_name)
os.makedirs(export_dir, exist_ok=True)

# === INDEX DES PANELS À EXTRAIRE ===

PANEL_IDS_GRAPH = [5, 10, 15]
PANEL_IDS_VALUES = [2, 3, 4, 7, 8, 9, 12, 13, 14]

# === EXPORT PRINCIPAL ===

def test_export_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 4000})
        page = context.new_page()

        # Connexion
        print("🔐 Connexion à Grafana...")
        page.goto(f"{grafana_base}/login")
        page.fill('input[name="user"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type=\"submit\"]')
        page.wait_for_timeout(2000)

        # Dashboard
        params = {
            "orgId": org_id,
            "from": from_str,
            "to": to_str,
        }
        url = f"{grafana_base}/d/{dashboard_uid}/{dashboard_slug}?{urlencode(params)}"
        print(f"➡️ Chargement du dashboard : {url}")
        page.goto(url)
        page.wait_for_timeout(15000)

        all_panels = page.locator("div.panel-container, div.react-grid-item")
        total = all_panels.count()
        print(f"🧩 Panels visibles détectés : {total}")

        values = {}
        images = []
        regex_valeur = re.compile(r"(.*?)([\-]?\d+[.,]?\d*\s?(?:kWh|MWh|%))", re.IGNORECASE)

        # === EXTRACTION VALEURS ===
        for i in PANEL_IDS_VALUES:
            if i >= total:
                print(f"⚠️ Panel valeur #{i} hors limite.")
                continue

            panel = all_panels.nth(i)
            raw = panel.text_content().strip()
            match = regex_valeur.search(raw)
            if match:
                label = match.group(1).strip() or f"valeur_{i}"
                val = match.group(2).strip()
                key = f"{i}_{label.replace(' ', '_')}"
                values[key] = val
                print(f"🔢 {key} = {val}")
            else:
                print(f"❌ Pas de valeur détectée dans panel #{i}")

        # === CAPTURE GRAPHIQUES SANS TITRE ===
        for i in PANEL_IDS_GRAPH:
            if i >= total:
                print(f"⚠️ Panel graphique #{i} hors limite.")
                continue

            panel = all_panels.nth(i)
            filename = f"graph_{i}.png"
            full_path = os.path.join(export_dir, filename)

            # Suppression fiable du titre (sans toucher à la légende)
            panel.evaluate("""
                (el) => {
                    const header = el.querySelector('[data-testid="header-container"]');
                    if (header) {
                        header.style.display = 'none';
                    }
                }
            """)

            panel.screenshot(path=full_path)
            images.append(filename)
            print(f"📸 Graphique capturé sans titre : {filename}")

        # === SAUVEGARDES ===

        with open(os.path.join(export_dir, "valeurs.json"), "w", encoding="utf-8") as f:
            json.dump(values, f, indent=2, ensure_ascii=False)

        with open(os.path.join(export_dir, "valeurs.csv"), "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Identifiant", "Valeur"])
            for k, v in values.items():
                writer.writerow([k, v])

        with open(os.path.join(export_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({
                "dashboard": dashboard_slug,
                "from": from_str,
                "to": to_str,
                "captured_graphs": images,
                "captured_values": list(values.keys())
            }, f, indent=2, ensure_ascii=False)

        print("✅ Export terminé.")
        browser.close()

# === LANCEMENT ===

if __name__ == "__main__":
    test_export_dashboard()
