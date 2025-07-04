# alias_resolver.py

alias_groups = {
    "mensuel": {
        "valeurs": {
            "1_Consommation_d'électricité": "consommation_reelle_elec",
            "2_Prédiction_d'électricité": "modele_predictif_elec",
            "3_Economie_d'électricité": "performance_contrat_percent_elec",
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec",
        },
        "images": {
            "superposition_predictif_reelle": "graph_5.png",
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
            "superposition_predictif_reelle_year": "graph_5.png",
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
