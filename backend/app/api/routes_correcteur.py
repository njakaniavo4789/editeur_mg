from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.correcteur import (
    corriger_mot, 
    verifier_texte,
    corriger_mot_avance,
    verifier_texte_avance
)

router = APIRouter()

class MotRequest(BaseModel):
    mot: str

class TexteRequest(BaseModel):
    texte: str

@router.post("/correct/mot")
def correct_mot(req: MotRequest):
    """Basic correction - spelling suggestions."""
    return {"mot": req.mot, "suggestions": corriger_mot(req.mot)}

@router.post("/correct/mot/advanced")
def correct_mot_advanced(req: MotRequest):
    """Advanced correction - spelling + phonotactics."""
    return corriger_mot_avance(req.mot)

@router.post("/correct/texte")
def correct_texte(req: TexteRequest):
    """Basic text verification."""
    return {"resultats": verifier_texte(req.texte)}

@router.post("/correct/texte/advanced")
def correct_texte_advanced(req: TexteRequest):
    """Advanced text verification with detailed phonotactics."""
    return {"resultats": verifier_texte_avance(req.texte)}
