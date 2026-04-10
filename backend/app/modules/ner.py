import json, os

def _charger_json(filename):
    path = os.path.join(os.path.dirname(__file__), f"../data/{filename}")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

VILLES = set(_charger_json("villes_mg.json"))
PERSONNES = set(_charger_json("noms_propres_mg.json"))

def detecter_entites(texte: str):
    entites = []
    for mot in texte.split():
        mot_clean = mot.strip(".,!?;:")
        if mot_clean in VILLES:
            entites.append({"mot": mot_clean, "type": "VILLE"})
        elif mot_clean in PERSONNES:
            entites.append({"mot": mot_clean, "type": "PERSONNE"})
    return entites
