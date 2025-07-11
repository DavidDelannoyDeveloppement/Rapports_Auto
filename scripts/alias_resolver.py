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
            #Conso réelle : 
            "2_Conso_Elec_+_Gaz": "consommation_reelle_combine",
            "1_Consommation_d'électricité": "consommation_reelle_elec",
            "8_Conso_Élec": "consommation_reelle_elec",
            "14_Conso_Gaz":"consommation_reelle_gaz",
            #Conso Prédite : 
            "3_Conso_Prédite_Elec_+_Gaz": "modele_predictif_combine",
            "2_Prédiction_d'électricité": "modele_predictif_elec",
            "9_Conso_Prédite_Élec": "modele_predictif_elec",
            "15_Conso_Prédite_Gaz":"modele_predictif_gaz",
            #Perf ou Éco : 
            "4_Eco_Elec_+_Gaz": "performance_contrat_percent_combine",
            "3_Economie_d'électricité": "performance_contrat_percent_elec",
            "10_Eco_Elec": "performance_contrat_percent_elec",
            "16_Eco_Gaz":"performance_contrat_percent_gaz",
            #Engagement : 
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec",
            "5_Engagement_Contractuel_Élec_+_Gaz":"engagement_contract_combine",

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
            #Conso réelle : 
            "2_Conso_Elec_+_Gaz": "consommation_reelle_combine_year",
            "1_Consommation_d'électricité": "consommation_reelle_elec_year",
            "8_Conso_Élec": "consommation_reelle_elec_year",
            "14_Conso_Gaz":"consommation_reelle_gaz_year",
            #Conso Prédite : 
            "3_Conso_Prédite_Elec_+_Gaz": "modele_predictif_combine_year",
            "2_Prédiction_d'électricité": "modele_predictif_elec_year",
            "9_Conso_Prédite_Élec": "modele_predictif_elec_year",
            "15_Conso_Prédite_Gaz":"modele_predictif_gaz_year",
            #Perf ou Éco : 
            "4_Eco_Elec_+_Gaz": "performance_contrat_percent_combine_year",
            "3_Economie_d'électricité": "performance_contrat_percent_elec_year",
            "10_Eco_Elec": "performance_contrat_percent_elec_year",
            "16_Eco_Gaz":"performance_contrat_percent_gaz_year",
            #Engagement : 
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec_year",
            "5_Engagement_Contractuel_Élec_+_Gaz":"engagement_contract_combine_year",

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
