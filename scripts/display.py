def chercher_valeur(valeurs, possibles):
    for key in possibles:
        if key in valeurs:
            data = valeurs[key]
            if isinstance(data, dict):
                val = float(data.get("valeur", 0))
                unit = data.get("unite", "").strip().lower()
                # Conversion vers kWh si besoin
                if unit == "mwh":
                    val *= 1000
                elif unit == "wh":
                    val /= 1000
                # sinon déjà en kWh ou inconnu (on laisse tel quel)
                return val
            else:
                return float(data)
    # print("🔎 Clés possibles testées :", possibles)
    # print("📦 Clés disponibles :", list(valeurs.keys()))        
    raise KeyError("Aucune des clés possibles trouvée.")


# Calcul Perf ou Éco Combiné
def performance_kwh(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Conso Elec + Gaz", "2_Conso_Elec_+_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction Elec + Gaz", "3_Conso_Prédite_Elec_+_Gaz"
        ])
        ecart_kwh = abs(prediction - consommation)
        ecart_mwh = ecart_kwh / 1000  # Conversion finale
        return f"{ecart_mwh:.1f}"
    except Exception:
        return "N/A"

def performance_kwh_year(valeurs):
    return performance_kwh(valeurs)


# Calcul Perf ou Éco Élec
def performance_kwh_elec(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_d'électricité", "8_Conso_Élec"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_d'électricité", "9_Conso_Prédite_Élec"
        ])
        ecart_kwh = abs(prediction - consommation)
        ecart_mwh = ecart_kwh / 1000  # Conversion finale
        return f"{ecart_mwh:.1f}"
    except Exception:
        return "N/A"

def performance_kwh_elec_year(valeurs):
    return performance_kwh_elec(valeurs)


# Calcul Perf ou Éco Gaz
def performance_kwh_gaz(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_de_gaz", "14_Conso_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_de_gaz","15_Conso_Prédite_Gaz"
        ])
        ecart_kwh = abs(prediction - consommation)
        ecart_mwh = ecart_kwh / 1000  # Conversion finale
        return f"{ecart_mwh:.1f}"
    except Exception:
        return "N/A"

def performance_kwh_gaz_year(valeurs):
    return performance_kwh_gaz(valeurs)


# Calcul Gain Combiné
def gain_perte(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Conso Elec + Gaz","2_Conso_Elec_+_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction Elec + Gaz","3_Conso_Prédite_Elec_+_Gaz"
        ])
        return "un Gain" if prediction - consommation >= 0 else "une Perte"
    except Exception:
        return "Erreur"

def gain_perte_year(valeurs):
    return gain_perte(valeurs)


# Calcul Gain Élec
def gain_perte_elec(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_d'électricité", "8_Conso_Élec"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_d'électricité", "9_Conso_Prédite_Élec"
        ])
        return "un Gain" if prediction - consommation >= 0 else "une Perte"
    except Exception:
        return "Erreur"

def gain_perte_elec_year(valeurs):
    return gain_perte_elec(valeurs)


# Calcul Gain Gaz
def gain_perte_gaz(valeurs):
    try:
        consommation = chercher_valeur(valeurs, [
            "1_Consommation_de_gaz", "14_Conso_Gaz"
        ])
        prediction = chercher_valeur(valeurs, [
            "2_Prédiction_de_gaz", "15_Conso_Prédite_Gaz"
        ])
        return "un Gain" if prediction - consommation >= 0 else "une Perte"
    except Exception:
        return "Erreur"

def gain_perte_gaz_year(valeurs):
    return gain_perte_gaz(valeurs)



def engagement_color(valeurs):
    try:
        perf = chercher_valeur(valeurs, [
            "3_Economie_d'électricité", "3_Economie_de_gaz", "3_Economie Elec + Gaz",
            "4_Eco_Elec_+_Gaz"
        ])
        engag = chercher_valeur(valeurs, [
            "4_Engagement_Contractuel_Élec", "4_Engagement_Contractuel_Gaz",
            "4_Engagement_Contractuel_Elec+Gaz", "5_Engagement_Contractuel_Élec_+_Gaz"
        ])
        return "#00b050" if perf - engag >= 0 else "#c00000"
    except Exception:
        return "#000000"


def engagement_color_year(valeurs):
    return engagement_color(valeurs)


def eco_surconso(valeurs):
    try:
        perf = chercher_valeur(valeurs, [
            "3_Economie_d'électricité", "3_Economie_de_gaz", "3_Economie Elec + Gaz",
            "4_Eco_Elec_+_Gaz"
        ])
        return "d'Économie" if perf >= 0 else "de Surconsommation"
    except Exception:
        return "#Erreur"


def eco_surconso_year(valeurs):
    return eco_surconso(valeurs)
