import os
from flask import Flask, render_template, send_from_directory
from collections import defaultdict

# === Définir les bons chemins ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "app", "templates"))
STATIC_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "app", "static"))
PDF_BASE_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "pdf"))

# === Création de l'application Flask ===
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# === Fonction utilitaire pour structurer les PDF ===
def lister_pdfs():
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for client in os.listdir(PDF_BASE_DIR):
        client_path = os.path.join(PDF_BASE_DIR, client)
        if not os.path.isdir(client_path):
            continue

        client_key = client.lower()

        for contrat in os.listdir(client_path):
            contrat_path = os.path.join(client_path, contrat)
            if not os.path.isdir(contrat_path):
                continue

            for fichier in os.listdir(contrat_path):
                if not fichier.endswith(".pdf"):
                    continue

                parts = fichier[:-4].split("_")
                if len(parts) < 2:
                    continue

                mois = parts[1]
                chemin = f"pdf/{client_key}/{contrat}/{fichier}"
                data[client_key][contrat][mois].append(chemin)

    return data

# === Page d'accueil (librairie admin) ===
@app.route("/")
def accueil():
    data = lister_pdfs()
    return render_template("librairie.html", data=data, mode="admin")

# === Page client dédiée (Alvend, ITM, Quercy) ===
@app.route("/librairie/<client>")
def page_client(client):
    client = client.lower()
    data = lister_pdfs()
    contrats = data.get(client, {})
    return render_template("librairie.html", data=contrats, mode="client", client=client)


# === Pour servir les fichiers PDF si besoin ===
@app.route("/pdf/<client>/<contrat>/<fichier>")
def telecharger_pdf(client, contrat, fichier):
    dossier = os.path.join(PDF_BASE_DIR, client, contrat)
    return send_from_directory(dossier, fichier)

# === Point d’entrée principal ===
if __name__ == "__main__":
    app.run(debug=True)
