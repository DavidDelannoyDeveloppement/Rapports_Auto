# alias_resolver.py
import os
import copy

# Noms d'affichage des contrats (inchangé)
image_aliases = {
    "Alvend_Conditionnement": "Conditionnement",
    "Alvend_Stockage": "Stockage",
    "ITM_Auxi": "ITM Auxi-le-Château",
    "ITM_Doullens": "ITM Doullens",
    "ITM_Gouvieux": "ITM Gouvieux",
    "ITM_Lambersart": "ITM Lambersart",
    "ITM_Le_Quesnoy": "ITM Le Quesnoy",
    "ITM_Montigny": "ITM Montigny",
    "ITM_PAM": "ITM Pont-à-Marcq",
    "Quercy_Cholet2": "Quercy Cholet2",
    "Quercy_Wissous": "Quercy Wissous",
    "Quercy_Ecouflant": "Quercy Ecouflant",
    "Quercy_Guilmot_Gaudais": "Quercy Guilmot Gaudais",
    "Leclerc_NLM": "Leclerc Nœux-les-Mines",
    "Leclerc_Vouziers": "Leclerc Vouziers",
    "Eiffage_Clinique_Union":"Clinique de l'Union",
    "Super_U_Frignicourt":"Super U Frignicourt"

}

# Alias par type de dashboard (base, pour tous les contrats)
alias_groups = {
    "mensuel": {
        "valeurs": {
            # Conso réelle :
            "2_Conso_Elec_+_Gaz": "consommation_reelle_combine",
            "1_Consommation_d'électricité": "consommation_reelle_elec",
            "8_Conso_Élec": "consommation_reelle_elec",
            "2_Conso_Élec": "consommation_reelle_elec",
            "8_Conso_Gaz":"consommation_reelle_gaz",
            "2_Conso_Gaz":"consommation_reelle_gaz",
            "14_Conso_Gaz":"consommation_reelle_gaz",
            # Conso Prédite :
            "3_Conso_Prédite_Elec_+_Gaz": "modele_predictif_combine",
            "2_Prédiction_d'électricité": "modele_predictif_elec",
            "3_Conso_Prédite_Élec": "modele_predictif_elec",
            "9_Conso_Prédite_Élec": "modele_predictif_elec",
            "9_Conso_Prédite_Gaz":"modele_predictif_gaz",
            "3_Conso_Prédite_Gaz":"modele_predictif_gaz",
            "15_Conso_Prédite_Gaz":"modele_predictif_gaz",
            # Perf ou Éco :
            "4_Eco_Elec_+_Gaz": "performance_contrat_percent_combine",
            "3_Economie_d'électricité": "performance_contrat_percent_elec",
            "4_Eco_Elec": "performance_contrat_percent_elec",
            "10_Eco_Elec": "performance_contrat_percent_elec",
            "16_Eco_Gaz":"performance_contrat_percent_gaz",
            "10_Eco_Gaz":"performance_contrat_percent_gaz",
            "4_Eco_Gaz":"performance_contrat_percent_gaz",
            # Engagement :
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec",
            "5_Engagement_Contractuel_Élec": "engagement_contract_elec",
            "5_Engagement_Contractuel_Élec_+_Gaz":"engagement_contract_combine",
            "11_Engagement_Contractuel_Gaz":"engagement_contract_gaz",
            "5_Engagement_Contractuel_Gaz":"engagement_contract_gaz"

        },
        "images": {
            "superposition_predictif_reelle_alvend": "graph_5.png",
            "superposition_predictif_reelle_itm": "graph_6.png",
            "superposition_predictif_reelle_quercy": "graph_6.png",
            "superposition_predictif_reelle_super_u_frignicourt": "graph_6.png",
            "superposition_predictif_reelle_elec_itm": "graph_12.png",
            "superposition_predictif_reelle_elec_separe_itm": "graph_6.png",
            "superposition_predictif_reelle_gaz_separe_itm": "graph_12.png",
            "superposition_predictif_reelle_gaz_itm": "graph_18.png",
        }
    },
    "annuel": {
        "valeurs": {
            # Conso réelle :
            "2_Conso_Elec_+_Gaz": "consommation_reelle_combine_year",
            "1_Consommation_d'électricité": "consommation_reelle_elec_year",
            "2_Conso_Élec": "consommation_reelle_elec_year",
            "8_Conso_Gaz":"consommation_reelle_gaz_year",
            "8_Conso_Élec": "consommation_reelle_elec_year",
            "14_Conso_Gaz":"consommation_reelle_gaz_year",
            "2_Conso_Gaz":"consommation_reelle_gaz_year",
            # Conso Prédite :
            "3_Conso_Prédite_Elec_+_Gaz": "modele_predictif_combine_year",
            "2_Prédiction_d'électricité": "modele_predictif_elec_year",
            "3_Conso_Prédite_Élec": "modele_predictif_elec_year",
            "9_Conso_Prédite_Élec": "modele_predictif_elec_year",
            "9_Conso_Prédite_Gaz":"modele_predictif_gaz_year",
            "15_Conso_Prédite_Gaz":"modele_predictif_gaz_year",
            "3_Conso_Prédite_Gaz":"modele_predictif_gaz_year",
            # Perf ou Éco :
            "4_Eco_Elec_+_Gaz": "performance_contrat_percent_combine_year",
            "3_Economie_d'électricité": "performance_contrat_percent_elec_year",
            "4_Eco_Elec": "performance_contrat_percent_elec_year",
            "10_Eco_Gaz":"performance_contrat_percent_gaz_year",
            "10_Eco_Elec": "performance_contrat_percent_elec_year",
            "16_Eco_Gaz":"performance_contrat_percent_gaz_year",
            "4_Eco_Gaz":"performance_contrat_percent_gaz_year",
            # Engagement :
            "4_Engagement_Contractuel_Élec": "engagement_contract_elec_year",
            "5_Engagement_Contractuel_Élec": "engagement_contract_elec_year",
            "11_Engagement_Contractuel_Gaz":"engagement_contract_gaz_year",
            "5_Engagement_Contractuel_Gaz":"engagement_contract_gaz_year",
            "5_Engagement_Contractuel_Élec_+_Gaz":"engagement_contract_combine_year",
        },
        "images": {
            "superposition_predictif_reelle_year_alvend": "graph_5.png",
            "superposition_predictif_reelle_year_itm": "graph_6.png",
            "superposition_predictif_reelle_year_quercy": "graph_6.png",
            "superposition_predictif_reelle_year_super_u_frignicourt": "graph_6.png",
            "superposition_predictif_reelle_elec_year_itm": "graph_12.png",
            "superposition_predictif_reelle_elec_separe_year_itm": "graph_6.png",
            "superposition_predictif_reelle_gaz_separe_year_itm": "graph_12.png",
            "superposition_predictif_reelle_gaz_year_itm": "graph_18.png",
        }
    },
    "analyse": {
        "valeurs": {},
        "images": {
            "temperatures": "graph_1.png",
            "temperatures_process": "graph_1.png",
            "temperatures_opt":"graph_2.png",
            "mode_fonctionnement_alvend": "graph_2.png",
            "mode_fonctionnement": "graph_3.png",
            "taux_compression_alvend": "graph_3.png",
            "taux_compression": "graph_4.png",
            "delta_temperatures":"graph_6.png",
            "sante_circuit_1": "graph_4.png",
            "sante_circuit_2": "graph_5.png",
            "intensite_compresseurs": "graph_7.png",
            "optimisation_energetique": "graph_9.png",
            "rendement_compresseur": "graph_10.png",
        }
    },
    "performances": {
        "valeurs": {},
        "images": {
            "COP": "graph_1.png",
            "EER": "graph_2.png",
            "taux_recup_chaleur": "graph_3.png",
            "puissances_recup_chaleur": "graph_4.png",
        }
    }
}


leclerc_vouziers_overrides = {
    "analyse": {
        "temperatures_process": "graph_1.png",
        "temperatures_process_2": "graph_2.png",
        "temperatures_opt": "graph_3.png",
        "temperatures_opt_2": "graph_4.png",
        "mode_fonctionnement": "graph_5.png",
        "mode_fonctionnement_2": "graph_6.png",
        "taux_compression": "graph_7.png",
        "taux_compression_2": "graph_8.png",
        "delta_temperatures": "graph_11.png",
        "delta_temperatures_2": "graph_12.png",
    },
    "performances": {
        "COP": "graph_1.png",
        "COP_2": "graph_2.png",
        "EER": "graph_3.png",
        "EER_2": "graph_4.png",
        "taux_recup_chaleur": "graph_5.png",
        "taux_recup_chaleur_2": "graph_6.png",
        "puissances_recup_chaleur": "graph_7.png",
        "puissances_recup_chaleur_2": "graph_8.png",
    }
}

eiffage_clinique_union_overrides = {
    "mensuel": {
        "valeurs": {
        "1_Consommation_de_Gaz":"consommation_reelle_gaz",
        "2_Prédiction_de_Gaz":"modele_predictif_gaz",
        "3_Economie_de_Gaz":"performance_contrat_percent_gaz",
        "4_Engagement_Contractuel_Gaz":"engagement_contract_gaz"
        },
        "images": {
            "superposition_predictif_reelle_eiffage":"graph_5.png"
        }
    },
    "annuel": {
        "valeurs": {
        "1_Consommation_de_Gaz":"consommation_reelle_gaz_year",
        "2_Prédiction_de_Gaz":"modele_predictif_gaz_year",
        "3_Economie_de_Gaz":"performance_contrat_percent_gaz_year",
        "4_Engagement_Contractuel_Gaz":"engagement_contract_gaz_year"
        },
        "images": {
            "superposition_predictif_reelle_2_eiffage":"graph_6.png"
        }
    },
    "analyse": {},
    "performances": {
        "images": {
            "puissance_thermique":"graph_1.png",
            "capacite_pac":"graph_2.png",
            "demarrages_journaliers":"graph_3.png",
            "cop_pac":"graph_4.png",
            "temperatures_pac":"graph_5.png",
            "capacite_gf1":"graph_6.png",
            "capacite_gf2":"graph_7.png",
        }
    }
}

def _is_vouziers_context(dashboard_name: str) -> bool:
    name = (dashboard_name or "").lower()
    env_flag = os.getenv("CURRENT_CONTRACT", "").strip().lower()
    return ("vouziers" in name) or (env_flag == "leclerc_vouziers")

def _is_eiffage_union_context(dashboard_name: str) -> bool:
    name = (dashboard_name or "").lower().replace(" ", "_")
    env_flag = os.getenv("CURRENT_CONTRACT", "").strip().lower()
    return ("eiffage" in name and ("union" in name or "clinique" in name)) or (env_flag == "eiffage_clinique_union")

def resolve_alias_map(dashboard_name: str) -> dict:
    name = (dashboard_name or "").lower()
    if "analyse" in name or "operationnelle" in name:
        base = copy.deepcopy(alias_groups["analyse"])
        section = "analyse"
    elif "annuel" in name:
        base = copy.deepcopy(alias_groups["annuel"])
        section = "annuel"
    elif "performances" in name:
        base = copy.deepcopy(alias_groups["performances"])
        section = "performances"
    else:
        base = copy.deepcopy(alias_groups["mensuel"])
        section = "mensuel"

    if section in ("analyse", "performances") and _is_vouziers_context(dashboard_name):
        override = leclerc_vouziers_overrides.get(section, {})
        base.setdefault("images", {})
        base["images"].update(override)

    if _is_eiffage_union_context(dashboard_name):
        override = eiffage_clinique_union_overrides.get(section, {})
        if "images" in override:
            base.setdefault("images", {})
            base["images"].update(override["images"])
        if "valeurs" in override:
            base.setdefault("valeurs", {})
            base["valeurs"].update(override["valeurs"])

    return base

