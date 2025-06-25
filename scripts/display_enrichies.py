def enrichir_valeurs(valeurs):
    enrichies = {}

    # 1. Copier toutes les valeurs brutes dans le contexte
    for key, val in valeurs.items():
        enrichies[key] = val

    # 2. Calcul dynamique de performance (mensuel, annuel, gaz, elec...)
    def eval_conformite(perf_key, engag_key, color_key, eco_key, gain_key):
        try:
            perf = float(valeurs.get(perf_key, 0))
            engag = float(valeurs.get(engag_key, 0))
            delta = perf - engag
            enrichies[color_key] = "#00b050" if delta >= 0 else "#c00000"
            enrichies[eco_key] = "Économie" if delta >= 0 else "Surconsommation"
            enrichies[gain_key] = "un gain" if delta >= 0 else "une perte"
        except:
            enrichies[color_key] = "#000000"
            enrichies[eco_key] = ""
            enrichies[gain_key] = ""

    # 3. Appliquer la logique à différents cas
    eval_conformite("performance_contrat_percent", "engagement_contract", "conforme_color", "eco_surconso", "gain_perte")
    eval_conformite("performance_contrat_percent_year", "engagement_contract", "conforme_color_year", "eco_surconso_year", "gain_perte_year")
    eval_conformite("performance_contrat_percent_elec", "engagement_contract_elec", "conforme_color_elec", "eco_surconso_elec", "gain_perte_elec")
    eval_conformite("performance_contrat_percent_year_elec", "engagement_contract_elec", "conforme_color_year_elec", "eco_surconso_year_elec", "gain_perte_year_elec")
    eval_conformite("performance_contrat_percent_gaz", "engagement_contract_gaz", "conforme_color_gaz", "eco_surconso_gaz", "gain_perte_gaz")
    eval_conformite("performance_contrat_percent_year_gaz", "engagement_contract_gaz", "conforme_color_year_gaz", "eco_surconso_year_gaz", "gain_perte_year_gaz")

    # 4. Alias explicites pour correspondance HTML <-> valeurs.json
    alias_map = {
        "1_Consommation_d'électricité":"consommation_reelle_elec",
        "3_Economie_d'électricité": "performance_contrat_percent",
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

    # 5. Alias pour certaines images si présentes dans les valeurs
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
