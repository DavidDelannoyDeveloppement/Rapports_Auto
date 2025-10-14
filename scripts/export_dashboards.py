import os
import json
import re
import unicodedata
import time
from datetime import datetime, timedelta, timezone
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
if not username or not password:
    raise ValueError("❌ Les identifiants Grafana ne sont pas définis dans le fichier .env.")

# === CHARGEMENT DU FICHIER CONTRATS ===
excel_path = os.path.join(project_root, "data", "Contrats_FiTT.xlsx")
df = pd.read_excel(excel_path)
df.ffill(inplace=True)

# === DÉTECTION PÉRIODE RÉFÉRENCE ===
def get_previous_month_range():
    return periode_manuelle if 'periode_manuelle' in globals() else _get_default_previous_month_range()

def _get_default_previous_month_range():
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

# =====================================================================
#                   TIMEOUTS & TEMPOS (ajouts)
# =====================================================================
NAV_TIMEOUT = 40_000          # navigation lourde Grafana
PANEL_TIMEOUT = 20_000        # attente d'un panel individuel
POST_LOGIN_PAUSE = 3_000      # souffle après login
POST_RELOAD_PAUSE = 20_000    # temps après reload pour stabiliser
SCROLL_STEP = 1200            # px par scroll
SCROLL_PAUSE = 600            # pause entre scrolls

# =====================================================================
#                   HELPERS (ajouts)
# =====================================================================
def wait_until_panels_listed(page):
    """Attend que la liste de panels soit présente et visible."""
    locator = page.locator("div.panel-container, div.react-grid-item")
    try:
        locator.first.wait_for(state="visible", timeout=PANEL_TIMEOUT)
    except Exception:
        # S'il n'y a pas encore de panel visible, attend que >0 existent dans le DOM
        page.wait_for_function(
            """() => document.querySelectorAll('div.panel-container, div.react-grid-item').length > 0""",
            timeout=PANEL_TIMEOUT
        )
    return page.locator("div.panel-container, div.react-grid-item")

def wait_until_panel_ready(panel):
    """Assure visibilité, scroll dans le viewport et présence éventuelle de canvas/svg."""
    panel.wait_for(state="visible", timeout=PANEL_TIMEOUT)
    panel.scroll_into_view_if_needed(timeout=PANEL_TIMEOUT)
    # Forcer le layout
    try:
        panel.bounding_box()
    except Exception:
        pass
    # Attendre un canvas/svg si c'est un graph (toléré si stat/table)
    try:
        panel.locator("canvas, svg").first.wait_for(state="visible", timeout=PANEL_TIMEOUT // 2)
    except Exception:
        pass
    # petite pause pour finir les rendus
    time.sleep(0.2)

def slow_scroll_through_dashboard(page):
    """Scroll progressif sur toute la page pour déclencher les rendus lazy."""
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.3)
    total_height = page.evaluate("() => document.body.scrollHeight")
    y = 0
    while y < total_height:
        y += SCROLL_STEP
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(SCROLL_PAUSE)
        total_height = page.evaluate("() => document.body.scrollHeight")
    # Remonter légèrement pour stabiliser
    page.evaluate("window.scrollTo(0, Math.max(document.body.scrollHeight - 800, 0))")
    page.wait_for_timeout(800)

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
        context = browser.new_context(viewport={"width": 1920, "height": 5000})
        context.set_default_timeout(NAV_TIMEOUT)
        page = context.new_page()
        page.set_default_timeout(NAV_TIMEOUT)

        print("🔐 Connexion à Grafana...")
        page.goto(f"{grafana_base}/login", wait_until="domcontentloaded")
        page.fill('input[name="user"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(POST_LOGIN_PAUSE)

        print("🧼 Nettoyage état précédent (about:blank)...")
        page.goto("about:blank", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # Conversion en timestamp Unix (millisecondes)
        from_epoch = int((pd.to_datetime(from_str) - pd.Timedelta(hours=2)).timestamp() * 1000)
        to_epoch   = int((pd.to_datetime(to_str)   - pd.Timedelta(hours=2)).timestamp() * 1000)

        url = f"{grafana_base}/d/{uid}/{slug}?orgId=1&from={from_epoch}&to={to_epoch}"
        print(f"➡️ Chargement du dashboard : {url}")
        page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT)

        current_url = page.url
        expected_slug = normalize_slug(slug)
        if expected_slug not in current_url:
            print(f"❌ Mismatch dashboard : attendu '{expected_slug}', mais trouvé : '{current_url}'")
            return

        page.reload(wait_until="networkidle", timeout=NAV_TIMEOUT)
        page.wait_for_timeout(POST_RELOAD_PAUSE)

        all_panels = wait_until_panels_listed(page)
        total = all_panels.count()
        print(f"🔎 Panels détectés : {total}")

        # Déclencher le rendu de tous les panels en scrollant
        slow_scroll_through_dashboard(page)

        # Recompter après scroll (le layout peut évoluer)
        all_panels = page.locator("div.panel-container, div.react-grid-item")
        total = all_panels.count()
        print(f"🔁 Panels comptés après scroll : {total}")

        values = {}
        images = []

        for pid, ptype in zip(panel_ids, panel_types):
            print(f"   ▶️ Panel #{pid} ({ptype})...")

            if pid >= total:
                print(f"   ⚠️ Panel #{pid} hors limite ({total} max)")
                continue

            panel = all_panels.nth(pid)
            try:
                wait_until_panel_ready(panel)
            except Exception as e:
                print(f"   ⚠️ Panel #{pid} pas prêt dans les temps : {e}")
                continue

            if ptype == "graph":
                # Masquer l'entête (si présent) pour des captures nettes
                try:
                    panel.evaluate("""
                        (el) => {
                            const header = el.querySelector('[data-testid="header-container"]');
                            if (header) header.style.display = 'none';
                        }
                    """)
                except Exception:
                    pass

                path = os.path.join(export_dir, f"graph_{pid}.png")
                handle = panel.element_handle()
                if handle:
                    try:
                        page.wait_for_timeout(600)  # micro-stabilisation des courbes
                        handle.screenshot(path=path)
                        images.append(f"graph_{pid}.png")
                        print(f"   📸 Graphique capturé : graph_{pid}.png")
                    except Exception as e:
                        print(f"❌ Erreur capture panel #{pid} : {e}")
                else:
                    print(f"❌ Panel #{pid} introuvable via element_handle()")

            elif ptype == "stat":
                raw = panel.text_content().strip()
                match = re.search(r"(.*?)([-]?\d+[.,]?\d*)\s?(kWh|GWh|MWh|%|€|kW)?", raw)
                if match:
                    label = match.group(1).strip() or f"valeur_{pid}"
                    val = match.group(2).strip()
                    unit = match.group(3) or ""
                    key = f"{pid}_{label.replace(' ', '_')}"
                    values[key] = {
                        "valeur": val,
                        "unite": unit
                    }
                    print(f"   🔢 Valeur extraite : {key} = {val} {unit}")
                else:
                    print(f"   ❌ Aucune valeur détectée dans panel #{pid}")

            elif ptype == "table":
                handle = panel.element_handle()
                if handle:
                    rows = panel.locator('div[role="row"]')
                    try:
                        rows.first.wait_for(state="visible", timeout=PANEL_TIMEOUT // 2)
                    except Exception:
                        pass
                    nb_rows = rows.count()
                    colonnes = [
                        "Circuit",
                        "Temps de fonctionnement total",
                        "Nombre de démarrage",
                        "Temps moyen de fonctionnement"
                    ]
                    table_data = []
                    for i in range(nb_rows):
                        cellules = rows.nth(i).locator('div[role="cell"]')
                        cell_count = cellules.count()
                        valeurs = [cellules.nth(j).inner_text().strip() for j in range(cell_count)]
                        if len(valeurs) == len(colonnes):
                            ligne = dict(zip(colonnes, valeurs))
                            table_data.append(ligne)
                        else:
                            print(f"   ⚠️ Ligne {i+1} ignorée (colonnes inattendues : {cell_count})")

                    key = f"{pid}_table_panel"
                    values[key] = table_data
                    print(f"   📋 Table extraite : {len(table_data)} lignes")
                else:
                    print(f"❌ Panel table #{pid} introuvable via element_handle()")

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
    periode_reference_short = mois_precedent[1].strftime("%y-%m")

    groupes = df.groupby(["Contrat", "UID Dashboard", "Nom du Dashboard"])

    total = 0
    erreurs = []

    for (contrat, uid, slug), group in groupes:
        if contrats_specifiques and contrat not in contrats_specifiques:
            continue

        panel_ids = group["ID Panel à extraire"].tolist()
        panel_types = group["Nature du panel"].tolist()
        date_debut = group["Date Début"].iloc[0]

        if isinstance(date_debut, str) and "enregistré" in date_debut.lower():
            from_str = mois_precedent[0].strftime("%Y-%m-%dT00:00:00Z")
            to_str = mois_precedent[1].strftime("%Y-%m-%dT23:59:59Z")
        else:
            try:
                from_dt = pd.to_datetime(date_debut)
                from_str = from_dt.strftime("%Y-%m-%dT00:00:00Z")
                to_str = mois_precedent[1].strftime("%Y-%m-%dT23:59:59Z")
            except:
                from_str = mois_precedent[0].strftime("%Y-%m-%dT00:00:00Z")
                to_str = mois_precedent[1].strftime("%Y-%m-%dT23:59:59Z")

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
    print(f"📁 Dashboards exportés : {total}")
    print(f"❌ Échecs détectés : {len(erreurs)}")
    if erreurs:
        print("🔎 Dashboards en erreur :", ", ".join(erreurs))

# === LANCEMENT + ARGUMENTS ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--periode", help="Période au format AAAA-MM", default=None)
    parser.add_argument("--contrat", action="append", help="Nom du contrat à traiter (répétable)")
    args = parser.parse_args()

    if args.periode:
        try:
            mois = datetime.strptime(args.periode, "%Y-%m")
            start = mois.replace(day=1)
            end = (mois.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            periode_manuelle = (start, end)
        except ValueError:
            print("❌ Format de période invalide. Format attendu : AAAA-MM")
            exit(1)
    else:
        periode_manuelle = _get_default_previous_month_range()

    contrats_specifiques = args.contrat if args.contrat else []

    main()
