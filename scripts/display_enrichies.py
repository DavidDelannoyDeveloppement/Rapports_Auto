import os
import json
from export_dashboards import normalize_slug
from alias_resolver import resolve_alias_map
from display import (
    performance_kwh, gain_perte, engagement_color, eco_surconso,
    performance_kwh_year, gain_perte_year, engagement_color_year, eco_surconso_year
)

def enrichir_valeurs(valeurs, meta_path=None, client_dir="unknown_client", periode="00-00"):
    enrichies = {}

    dashboard_slug = "default"
    dashboard_dir = "dashboard"
    dashboard_name = "unknown"

    # Lecture du nom du dashboard depuis le fichier meta
    if meta_path and os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                dashboard_name = meta.get("dashboard", "")
                dashboard_slug = normalize_slug(dashboard_name)
                dashboard_dir = meta.get("dashboard_dir", dashboard_slug)
        except Exception as e:
            print(f"⚠️ Erreur lecture meta.json : {e}")

    # Construction du chemin image de base
    base_image_path = f"../../../exports/{client_dir}/{periode}/{dashboard_dir}"

    # Résolution des alias dynamiques (valeurs + images)
    alias_data = resolve_alias_map(dashboard_name)
    alias_map = alias_data.get("valeurs", {})
    image_aliases = alias_data.get("images", {})

    # Alias d'images : graph_5.png, etc.
    for alias, filename in image_aliases.items():
        enrichies[alias] = f"{base_image_path}/{filename}"

    # Alias de valeurs : 1_, 2_, etc.
    for original, alias in alias_map.items():
        if original in valeurs:
            valeur_brute = valeurs[original]
            if isinstance(valeur_brute, dict):
                enrichies[f"{alias}_val"] = valeur_brute.get("valeur", "")
                enrichies[f"{alias}_unit"] = valeur_brute.get("unite", "")
            else:
                enrichies[f"{alias}_val"] = valeur_brute
                enrichies[f"{alias}_unit"] = ""

    # Calculs dynamiques (peu importe le type de dashboard)
    enrichies["performance_contrat_kwh"] = performance_kwh(valeurs)
    enrichies["gain_perte"] = gain_perte(valeurs)
    enrichies["engagement_color"] = engagement_color(valeurs)
    enrichies["eco_surconso"] = eco_surconso(valeurs)

    enrichies["performance_contrat_kwh_year"] = performance_kwh_year(valeurs)
    enrichies["gain_perte_year"] = gain_perte_year(valeurs)
    enrichies["engagement_color_year"] = engagement_color_year(valeurs)
    enrichies["eco_surconso_year"] = eco_surconso_year(valeurs)

    return enrichies
