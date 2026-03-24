from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.correcteur import corriger_mot, verifier_texte

router = APIRouter()

class MotRequest(BaseModel):
    mot: str

class TexteRequest(BaseModel):
    texte: str

@router.post("/correct/mot")
def correct_mot(req: MotRequest):
    return {"mot": req.mot, "suggestions": corriger_mot(req.mot)}

@router.post("/correct/texte")
def correct_texte(req: TexteRequest):
    return {"resultats": verifier_texte(req.texte)}
