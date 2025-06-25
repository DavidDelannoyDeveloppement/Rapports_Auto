import os
import json
import re
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# === CHARGEMENT DU FICHIER CONFIG (.json) ===

script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
config_path = os.path.join(script_dir, "analyse_config.json")

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

dashboard_url = config["dashboard_url"]

# === EXTRACTION UID, SLUG ET PARAMS ===

parsed = urlparse(dashboard_url)
path_parts = parsed.path.strip("/").split("/")

try:
    uid = path_parts[1]
    slug = path_parts[2]
except IndexError:
    raise ValueError("URL mal formatée : impossible d'extraire l'UID et le slug.")

query_params = parse_qs(parsed.query)
from_str = query_params.get("from", [""])[0]
to_str = query_params.get("to", [""])[0]

# === VARIABLES ENV ===

dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

username = os.getenv("GRAFANA_USER")
password = os.getenv("GRAFANA_PASS")

# === ANALYSE DU DASHBOARD ===

def analyse_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 4000})
        page = context.new_page()

        # Connexion
        print("🔐 Connexion à Grafana...")
        page.goto("https://view.preprod.fitt-solutions.fr/login")
        page.fill('input[name="user"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)

        # Accès au dashboard
        print(f"➡️ Analyse de : {dashboard_url}")
        page.goto(dashboard_url)
        page.wait_for_timeout(15000)

        panels = page.locator("div.panel-container, div.react-grid-item")
        total = panels.count()
        print(f"🔎 Panels visibles : {total}")

        result = []

        for i in range(total):
            panel = panels.nth(i)

            try:
                title = panel.locator('[data-testid="panel-title"]').inner_text(timeout=1000)
            except:
                title = "(sans titre)"

            try:
                content = panel.text_content().strip()
            except:
                content = ""

            inner_html = panel.inner_html()

            # === DÉTECTION TYPE DE PANEL ===
            if "data-testid=\"panel-header-row\"" in inner_html:
                panel_type = "row"
            elif "data-testid=\"table-panel\"" in inner_html or "role=\"table\"" in inner_html:
                panel_type = "table"
            elif any(kw in content.lower() for kw in ["kwh", "mwh", "%", "€", "kw", "conso", "puissance"]):
                panel_type = "stat"
            elif "canvas" in inner_html or "svg" in inner_html:
                panel_type = "graph"
            else:
                panel_type = "inconnu"

            result.append({
                "index": i,
                "title": title,
                "type": panel_type,
                "text": content[:300]
            })

            print(f"📌 Panel #{i} | {panel_type.upper()} | {title}")

        # Sauvegarde
        export_dir = os.path.join(project_root, "exports", "debug")
        os.makedirs(export_dir, exist_ok=True)
        safe_slug = re.sub(r"[^\w\-]", "_", slug)
        out_path = os.path.join(export_dir, f"analyse_{safe_slug}.json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Analyse sauvegardée ici : {out_path}")
        browser.close()

# === LANCEMENT ===

if __name__ == "__main__":
    analyse_dashboard()
