# alias_resolver.py

image_aliases = {
    "Alvend_Conditionnement": "Conditionnement",
    "Alvend_Stockage": "Stockage",
    "ITM_Doullens": "ITM Doullens",
    "ITM_Gouvieux": "ITM Gouvieux",
    "ITM_Lambersart": "ITM Lambersart",
    "ITM_Le_Quesnoy": "ITM Le Quesnoy",
    "ITM_Montigny": "ITM Montigny",
    "ITM_PAM": "ITM Pont-à-Marcq",
    "Quercy_Cholet2": "Quercy Cholet2",
    "Quercy_Guilmot_Gaudais": "Quercy Guilmot Gaudais",
    
}

alias_groups = {
    "mensuel": {
        "valeurs": {
            "1_Consommation_d'électricité": "consommation_reelle_elec",
            "2_Conso_Elec_+_Gaz": "consommation_reelle",
            "2_Prédiction_d'électricité": "modele_predictif_elec",
            "3_Conso_Prédite_Elec_+_Gaz": "modele_predictif",
            "3_Economie_d'électricité": "performance_contrat_percent_elec",
            "4_Eco_Elec_+_Gaz": "performance_contrat_percent",
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec",
            "5_Engagement_Contractuel_Élec_+_Gaz":"engagement_contract",
        },
        "images": {
            "superposition_predictif_reelle_alvend": "graph_5.png",
            "superposition_predictif_reelle_itm": "graph_6.png",
            "superposition_predictif_reelle_elec_itm": "graph_12.png",
            "superposition_predictif_reelle_gaz_itm": "graph_18.png",
        }
    },
    "annuel": {
        "valeurs": {
            "1_Consommation_d'électricité": "consommation_reelle_elec_year",
            "2_Prédiction_d'électricité": "modele_predictif_elec_year",
            "3_Economie_d'électricité": "performance_contrat_percent_elec_year",
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec_year",
        },
        "images": {
            "superposition_predictif_reelle_year_alvend": "graph_5.png",
            "superposition_predictif_reelle_year_itm": "graph_6.png",
            "superposition_predictif_reelle_elec_year_itm": "graph_12.png",
            "superposition_predictif_reelle_gaz_year_itm": "graph_18.png",
        }
    },
    "analyse": {
        "valeurs": {
            
        },
        "images": {
            "temperatures": "graph_1.png",
            "temperatures_process": "graph_2.png",
            "temperatures_opt":"graph_3.png,",
            "mode_fonctionnement_alvend": "graph_2.png",
            "mode_fonctionnement": "graph_3.png",
            "taux_compression_alvend": "graph_3.png",
            "taux_compression": "graph_4.png",
            "delta_temperatures":"graph_5.png",
            "sante_circuit_1": "graph_4.png",
            "sante_circuit_2": "graph_5.png",
            "intensite_compresseurs": "graph_7.png",
            "optimisation_energetique": "graph_9.png",
            "rendement_compresseur": "graph_10.png"
        }
    },
    "performances": {
        "valeurs": {
            
        },
        "images": {
            "COP": "graph_1.png",
            "EER": "graph_2.png",
            "taux_recup_chaleur": "graph_3.png",
            "puissances_recup_chaleur": "graph_4.png",
        }
    }
}


def resolve_alias_map(dashboard_name: str) -> dict:
    name = dashboard_name.lower()
    if "analyse" in name or "operationnelle" in name:
        return alias_groups["analyse"]
    elif "annuel" in name:
        return alias_groups["annuel"]
    else:
        return alias_groups["mensuel"]
