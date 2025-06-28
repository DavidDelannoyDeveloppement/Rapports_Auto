import os
import json
from export_dashboards import normalize_slug
from alias_resolver import image_aliases, resolve_alias_map
from display import performance_kwh, gain_perte, engagement_color, eco_surconso, performance_kwh_year, gain_perte_year, engagement_color_year, eco_surconso_year

def enrichir_valeurs(valeurs, meta_path=None, client_dir="unknown_client", periode="00-00"):
    enrichies = {}

    dashboard_slug = "default"
    dashboard_dir = "dashboard"
    dashboard_name = "unknown"

    if meta_path and os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                dashboard_name = meta.get("dashboard", "")
                dashboard_slug = normalize_slug(dashboard_name)
                dashboard_dir = meta.get("dashboard_dir", dashboard_slug)
        except:
            pass

    # Génère le préfixe du chemin commun
    base_image_path = f"../../../exports/{client_dir}/{periode}/{dashboard_dir}"

    # Images avec chemins complets
    for alias, filename in image_aliases.items():
        enrichies[alias] = f"{base_image_path}/{filename}"

    # Données brutes via alias dynamiques
    alias_map = resolve_alias_map(dashboard_name)
    for original, alias in alias_map.items():
        if original in valeurs:
            enrichies[alias] = valeurs[original]

    # Comparaisons dynamiques
        enrichies["performance_contrat_kwh"] = performance_kwh(valeurs)
        enrichies["gain_perte"] = gain_perte(valeurs)
        enrichies["engagement_color"] = engagement_color(valeurs)
        enrichies["eco_surconso"] = eco_surconso(valeurs)

        enrichies["performance_contrat_kwh_year"] = performance_kwh_year(valeurs)
        enrichies["gain_perte_year"] = gain_perte_year(valeurs)
        enrichies["engagement_color_year"] = engagement_color_year(valeurs)
        enrichies["eco_surconso_year"] = eco_surconso_year(valeurs)

    return enrichies
