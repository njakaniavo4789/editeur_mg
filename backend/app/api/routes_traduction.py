from fastapi import APIRouter
from pydantic import BaseModel
import json, csv, os

router = APIRouter()

DICO_JSON_PATH = os.path.join(os.path.dirname(__file__), "../data/dictionnaire_mg_fr.json")
DICO_CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/dico2.csv")
VILLES_PATH = os.path.join(os.path.dirname(__file__), "../data/villes_mg.json")
PERSONNES_PATH = os.path.join(os.path.dirname(__file__), "../data/noms_propres_mg.json")

def _charger_dictionnaire():
    dico = {}
    if os.path.exists(DICO_JSON_PATH):
        with open(DICO_JSON_PATH, encoding="utf-8") as f:
            dico.update(json.load(f))
    if os.path.exists(DICO_CSV_PATH):
        with open(DICO_CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mot = row.get("mot_malgache", "").strip().lower()
                trad = row.get("resume_francais", "").strip()
                if mot and trad:
                    dico[mot] = trad
    return dico

def _charger_liste_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return set(json.load(f))
    return set()

DICO_MG_FR = _charger_dictionnaire()
VILLES = _charger_liste_json(VILLES_PATH)
PERSONNES = _charger_liste_json(PERSONNES_PATH)

class AnalyseTexteRequest(BaseModel):
    texte: str

@router.post("/analyse/texte")
def analyser_texte(req: AnalyseTexteRequest):
    texte = req.texte.strip()
    if not texte:
        return {"mots": []}
    
    mots = texte.replace(',', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ').split()
    resultats = []
    
    for mot in mots:
        mot_clean = mot.strip().lower()
        if not mot_clean or len(mot_clean) < 2:
            continue
        
        mot_orig = mot.strip()
        
        entite = None
        if mot_clean in VILLES:
            entite = "VILLE"
        elif mot_clean in PERSONNES:
            entite = "PERSONNE"
        
        correction = None
        if mot_clean not in DICO_MG_FR:
            from rapidfuzz import process, utils
            suggestions = process.extract(mot_clean, list(DICO_MG_FR.keys()), limit=2, processor=utils.default_process)
            if suggestions and suggestions[0][1] > 70:
                correction = {"suggestions": [{"mot": s[0], "score": round(s[1], 0)} for s in suggestions[:2]]}
        
        lemma = None
        from app.modules.lemmatiseur import get_analyseur
        try:
            lemma = get_analyseur().analyser(mot_clean)
        except:
            pass
        
        traduction = DICO_MG_FR.get(mot_clean)
        
        resultats.append({
            "mot": mot_orig,
            "entite": entite,
            "correction": correction,
            "lemma": lemma,
            "traduction": traduction,
            "inDico": mot_clean in DICO_MG_FR
        })
    
    return {"mots": resultats, "texte": texte}

class TraductionRequest(BaseModel):
    mot: str
    source: str = "mg"
    cible: str = "fr"

@router.post("/translate")
def traduire(req: TraductionRequest):
    mot_lower = req.mot.lower().strip()
    
    if mot_lower in DICO_MG_FR:
        return {"mot": req.mot, "traduction": DICO_MG_FR[mot_lower]}
    
    if req.mot in DICO_MG_FR:
        return {"mot": req.mot, "traduction": DICO_MG_FR[req.mot]}
    
    for k, v in DICO_MG_FR.items():
        if mot_lower.startswith(k) or k.startswith(mot_lower):
            return {"mot": req.mot, "traduction": f"{v} (approx.)"}
    
    return {"mot": req.mot, "traduction": "Tsy hita ny fandikana"}