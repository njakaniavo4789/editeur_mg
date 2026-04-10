import json, os
from rapidfuzz import process, fuzz
from app.modules.phonotactique import verifier_phonotactique

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/dictionnaire_mg.json")

def _charger_dictionnaire():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, encoding="utf-8") as f:
            return list(json.load(f).keys())
    return []

DICTIONNAIRE = _charger_dictionnaire()

def corriger_mot(mot: str):
    if mot in DICTIONNAIRE:
        return []
    resultats = process.extract(mot, DICTIONNAIRE, scorer=fuzz.ratio, limit=5)
    return [r[0] for r in resultats if r[1] > 60]

def verifier_texte(texte: str):
    mots = texte.split()
    resultats = []
    for mot in mots:
        erreur_phono = verifier_phonotactique(mot)
        suggestions = corriger_mot(mot)
        if erreur_phono or suggestions:
            resultats.append({
                "mot": mot,
                "erreur_phonotactique": erreur_phono,
                "suggestions": suggestions
            })
    return resultats
