# alias_resolver.py

alias_groups = {
    "mensuel": {
        "1_Consommation_d'électricité": "consommation_reelle_elec",
        "2_Prédiction_d'électricité": "modele_predictif_elec",
        "3_Economie_d'électricité": "performance_contrat_percent_elec",
        "4_Engagement_Contractuel_Élec": "engagement_contract_elec",
    },
    "annuel": {
        "1_Consommation_d'électricité": "consommation_reelle_elec_year",
        "2_Prédiction_d'électricité": "modele_predictif_elec_year",
        "3_Economie_d'électricité": "performance_contrat_percent_elec_year",
        "4_Engagement_Contractuel_Élec": "engagement_contract_elec_year",
    },
}

image_aliases = {
    "superposition_predictif_reelle": "graph_5.png",
    "superposition_predictif_reelle_year": "graph_5.png",
}

def resolve_alias_map(dashboard_name: str) -> dict:
    name = dashboard_name.lower()
    if "annuel" in name:
        return alias_groups["annuel"]
    return alias_groups["mensuel"]














# alias_map.py

# data_aliases = {
#     "1_Consommation_d'électricité": "consommation_reelle_elec",
#     "2_Prédiction_d'électricité": "modele_predictif",
#     "3_Economie_d'électricité": "performance_contrat_percent",
#     "4_Engagement_Contractuel_Élec": "engagement_contract",
#     "1_Consommation_d'électricité":"consommation_reelle_year",
#     "4_Eco_Elec": "performance_contrat_percent_elec",
#     "9_Eco_Elec": "performance_contrat_percent_year_elec",
#     "14_Eco_Gaz": "performance_contrat_percent_year_gaz",
#     "2_Conso_Elec_+_Gaz": "conso_mixte",
#     "3_Conso_Prédite_Elec_+_Gaz": "conso_mixte_predite",
#     "4_Eco_Elec_+_Gaz": "eco_mixte",
#     "7_Conso_Élec": "conso_elec",
#     "8_Conso_Prédite_Élec": "conso_elec_predite",
#     "9_Eco_Elec": "eco_elec",
#     "12_Conso_Gaz": "conso_gaz",
#     "13_Conso_Prédite_Gaz": "conso_gaz_predite",
#     "14_Eco_Gaz": "eco_gaz"
# }

# image_aliases = {
#     "superposition_predictif_reelle":"graph_5.png",
#     "superposition_predictif_reelle_year":"graph_5.png",
#     "superposition_predictif_reelle_elec",
#     "superposition_predictif_reelle_year_elec",
#     "superposition_predictif_reelle_gaz",
#     "superposition_predictif_reelle_year_gaz",
#     "temperatures_process",
#     "temperatures_opt",
#     "mode_fonctionnement",
#     "taux_de_compression",
#     "delta_temperatures",
#     "COP",
#     "EER",
#     "taux_recup_chaleur",
#     "puissances_recup_chaleur"
# }
