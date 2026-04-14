from fastapi import APIRouter
from pydantic import BaseModel
import json, os

router = APIRouter()

DICO_PATH = os.path.join(os.path.dirname(__file__), "../data/dictionnaire_mg_fr.json")

def _charger_dictionnaire():
    if os.path.exists(DICO_PATH):
        with open(DICO_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

DICO_MG_FR = _charger_dictionnaire()

class TraductionRequest(BaseModel):
    mot: str
    source: str = "mg"
    cible: str = "fr"

@router.post("/translate")
def traduire(req: TraductionRequest):
    mot_lower = req.mot.lower().strip()
    
    # Try exact match
    if mot_lower in DICO_MG_FR:
        return {"mot": req.mot, "traduction": DICO_MG_FR[mot_lower]}
    
    # Try original case
    if req.mot in DICO_MG_FR:
        return {"mot": req.mot, "traduction": DICO_MG_FR[req.mot]}
    
    # Try partial match (prefix)
    for k, v in DICO_MG_FR.items():
        if mot_lower.startswith(k) or k.startswith(mot_lower):
            return {"mot": req.mot, "traduction": f"{v} (approx.)"}
    
    return {"mot": req.mot, "traduction": "Tsy hita ny fandikana"}
