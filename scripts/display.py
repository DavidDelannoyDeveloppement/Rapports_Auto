# def performance_kwh(valeurs, slug):
#     try:
#         prediction = float(valeurs.get("2_Prédiction_d'électricité", 0))
#         consommation = float(valeurs.get("1_Consommation_d'électricité", 0))
#         return f"{abs(round(prediction - consommation, 2)):.2f}"
#     except Exception:
#         return "N/A"

# def gain_perte(valeurs, slug):
#     try:
#         prediction = float(valeurs.get("2_Prédiction_d'électricité", 0))
#         consommation = float(valeurs.get("1_Consommation_d'électricité", 0))
#         return "un Gain" if prediction - consommation >= 0 else "une Perte"
#     except Exception:
#         return "Erreur"

# def engagement_color(valeurs, slug):
#     try:
#         perf = float(valeurs.get("3_Economie_d'électricité", 0))
#         engag = float(valeurs.get("4_Engagement_Contractuel_Élec", 0))
#         return "#00b050" if perf - engag >= 0 else "#c00000"
#     except Exception:
#         return "#000000"

# def eco_surconso(valeurs, slug):
#     try:
#         perf = float(valeurs.get("3_Economie_d'électricité", 0))
#         engag = float(valeurs.get("4_Engagement_Contractuel_Élec", 0))
#         return "Économie" if perf - engag >= 0 else "Surconsommation"
#     except Exception:
#         return "#Erreur"





def chercher_valeur(valeurs, possibles):
    """Retourne la première valeur trouvée parmi une liste de clés possibles."""
    for key in possibles:
        if key in valeurs:
            return float(valeurs[key])
    raise KeyError("Aucune des clés possibles trouvée.")

def performance_kwh(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_d'électricité",
            "1_Consommation_de_gaz",
            "1_Conso Elec + Gaz",
            "Cons_Élec",
            "Conso_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_d'électricité",
            "2_Prédiction_de_gaz",
            "2_Prédiction Elec + Gaz",
            "Préd_Élec",
            "Préd_Gaz"
        ])
        return f"{abs(prediction - consommation)}"
    except Exception:
        return "N/A"
    

def performance_kwh_year(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_d'électricité",
            "1_Consommation_de_gaz",
            "1_Conso Elec + Gaz",
            "Cons_Élec",
            "Conso_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_d'électricité",
            "2_Prédiction_de_gaz",
            "2_Prédiction Elec + Gaz",
            "Préd_Élec",
            "Préd_Gaz"
        ])
        return f"{abs(prediction - consommation)}"
    except Exception:
        return "N/A"


def gain_perte(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_d'électricité",
            "1_Consommation_de_gaz",
            "1_Conso Elec + Gaz",
            "Cons_Élec",
            "Conso_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_d'électricité",
            "2_Prédiction_de_gaz",
            "2_Prédiction Elec + Gaz",
            "Préd_Élec",
            "Préd_Gaz"
        ])
        return "un Gain" if prediction - consommation >= 0 else "une Perte"
    except Exception:
        return "Erreur"
    

def gain_perte_year(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_d'électricité",
            "1_Consommation_de_gaz",
            "1_Conso Elec + Gaz",
            "Cons_Élec",
            "Conso_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_d'électricité",
            "2_Prédiction_de_gaz",
            "2_Prédiction Elec + Gaz",
            "Préd_Élec",
            "Préd_Gaz"
        ])
        return "un Gain" if prediction - consommation >= 0 else "une Perte"
    except Exception:
        return "Erreur"


def engagement_color(valeurs):
    try:
        perf = chercher_valeur(valeurs, [
            "3_Economie_d'électricité",
            "3_Economie_de_gaz",
            "3_Economie Elec + Gaz"
        ])
        engag = chercher_valeur(valeurs, [
            "4_Engagement_Contractuel_Élec",
            "4_Engagement_Contractuel_Gaz",
            "4_Engagement_Contractuel_Elec+Gaz"
        ])
        return "#00b050" if perf - engag >= 0 else "#c00000"
    except Exception:
        return "#000000"
    

def engagement_color_year(valeurs):
    try:
        perf = chercher_valeur(valeurs, [
            "3_Economie_d'électricité",
            "3_Economie_de_gaz",
            "3_Economie Elec + Gaz"
        ])
        engag = chercher_valeur(valeurs, [
            "4_Engagement_Contractuel_Élec",
            "4_Engagement_Contractuel_Gaz",
            "4_Engagement_Contractuel_Elec+Gaz"
        ])
        return "#00b050" if perf - engag >= 0 else "#c00000"
    except Exception:
        return "#000000"
        

def eco_surconso(valeurs):
    try:
        perf = chercher_valeur(valeurs, [
            "3_Economie_d'électricité",
            "3_Economie_de_gaz",
            "3_Economie Elec + Gaz"
        ])
        engag = chercher_valeur(valeurs, [
            "4_Engagement_Contractuel_Élec",
            "4_Engagement_Contractuel_Gaz",
            "4_Engagement_Contractuel_Elec+Gaz"
        ])
        return "d'Économie" if perf - engag >= 0 else "de Surconsommation"
    except Exception:
        return "#Erreur"
    

def eco_surconso_year(valeurs):
    try:
        perf = chercher_valeur(valeurs, [
            "3_Economie_d'électricité",
            "3_Economie_de_gaz",
            "3_Economie Elec + Gaz"
        ])
        engag = chercher_valeur(valeurs, [
            "4_Engagement_Contractuel_Élec",
            "4_Engagement_Contractuel_Gaz",
            "4_Engagement_Contractuel_Elec+Gaz"
        ])
        return "d'Économie" if perf - engag >= 0 else "de Surconsommation"
    except Exception:
        return "#Erreur"
