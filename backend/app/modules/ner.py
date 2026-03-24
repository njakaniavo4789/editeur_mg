import json, os

def _charger_json(filename):
    path = os.path.join(os.path.dirname(__file__), f"../data/{filename}")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

VILLES    = set(v.lower() for v in _charger_json("villes_mg.json"))
PERSONNES = set(p.lower() for p in _charger_json("noms_propres_mg.json"))

def detecter_entites(texte: str):
    entites = []
    for mot in texte.split():
        mot_clean = mot.strip(".,!?;:")
        mot_lower = mot_clean.lower()
        if mot_lower in VILLES:
            entites.append({"mot": mot_clean, "type": "VILLE"})
        elif mot_lower in PERSONNES:
            entites.append({"mot": mot_clean, "type": "PERSONNE"})
    return entites
