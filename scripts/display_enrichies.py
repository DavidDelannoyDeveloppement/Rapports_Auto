def enrichir_valeurs(valeurs):
    enrichies = {}

    # Copier toutes les valeurs brutes dans le contexte
    for key, val in valeurs.items():
        enrichies[key] = val

    # Calcul de la différence prédiction - consommation (en valeur absolue)
    try:
        prediction = float(valeurs.get("2_Prédiction_d'électricité", 0))
        consommation = float(valeurs.get("1_Consommation_d'électricité", 0))
        diff = abs(round(prediction - consommation, 2))
        enrichies["performance_contrat_kwh"] = f"{diff:.2f}"
    except Exception:
        enrichies["performance_contrat_kwh"] = "N/A"

    # Texte gain/perte
    try:
        prediction = float(valeurs.get("2_Prédiction_d'électricité", 0))
        consommation = float(valeurs.get("1_Consommation_d'électricité", 0))
        diff = round(prediction - consommation, 2)
        enrichies["gain_perte"] = "un Gain" if diff >= 0 else "une Perte"
    except Exception:
        enrichies["gain_perte"] = "Erreur"

    # Couleur performance élec vs engagement
    try:
        perf = float(valeurs.get("3_Economie_d'électricité", 0))
        engag = float(valeurs.get("4_Engagement_Contractuel_Élec", 0))
        delta = perf - engag
        enrichies["engagement_color"] = "#00b050" if delta >= 0 else "#c00000"
    except Exception:
        enrichies["engagement_color"] = "#000000"

    # Texte surconso/éco
    try:
        perf = float(valeurs.get("3_Economie_d'électricité", 0))
        engag = float(valeurs.get("4_Engagement_Contractuel_Élec", 0))
        delta = perf - engag
        enrichies["eco_surconso"] = "Économie" if delta >= 0 else "Surconsommation"
    except:
        enrichies["eco_surconso"] = "#Erreur"

    # Alias explicites pour correspondance HTML <-> valeurs.json
    alias_map = {
        "1_Consommation_d'électricité": "consommation_reelle_elec",
        "2_Prédiction_d'électricité": "modele_predictif",
        "3_Economie_d'électricité": "performance_contrat_percent",
        "4_Engagement_Contractuel_Élec": "engagement_contract",
        "4_Eco_Elec": "performance_contrat_percent_elec",
        "9_Eco_Elec": "performance_contrat_percent_year_elec",
        "14_Eco_Gaz": "performance_contrat_percent_year_gaz",
        "2_Conso_Elec_+_Gaz": "conso_mixte",
        "3_Conso_Prédite_Elec_+_Gaz": "conso_mixte_predite",
        "4_Eco_Elec_+_Gaz": "eco_mixte",
        "7_Conso_Élec": "conso_elec",
        "8_Conso_Prédite_Élec": "conso_elec_predite",
        "9_Eco_Elec": "eco_elec",
        "12_Conso_Gaz": "conso_gaz",
        "13_Conso_Prédite_Gaz": "conso_gaz_predite",
        "14_Eco_Gaz": "eco_gaz"
    }
    for original, alias in alias_map.items():
        if original in valeurs:
            enrichies[alias] = valeurs[original]

    # Alias pour certaines images si présentes dans les valeurs
    image_aliases = [
        "superposition_predictif_reelle",
        "superposition_predictif_reelle_year",
        "superposition_predictif_reelle_elec",
        "superposition_predictif_reelle_year_elec",
        "superposition_predictif_reelle_gaz",
        "superposition_predictif_reelle_year_gaz",
        "temperatures_process",
        "temperatures_opt",
        "mode_fonctionnement",
        "taux_de_compression",
        "delta_temperatures",
        "COP",
        "EER",
        "taux_recup_chaleur",
        "puissances_recup_chaleur"
    ]

    for alias in image_aliases:
        if alias in valeurs:
            enrichies[alias] = valeurs[alias]

    return enrichies
