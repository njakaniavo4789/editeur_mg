from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.correcteur import corriger_mot, verifier_texte, get_correcteur

router = APIRouter()

class MotRequest(BaseModel):
    mot: str

class TexteRequest(BaseModel):
    texte: str

@router.post("/correct/mot")
def correct_mot(req: MotRequest):
    result = get_correcteur().corriger(req.mot)
    if result["correct"]:
        return {"mot": req.mot, "suggestions": []}
    return {"mot": req.mot, "suggestions": [s["mot"] for s in result["suggestions"]]}

@router.post("/correct/mot/detail")
def correct_mot_detail(req: MotRequest):
    return get_correcteur().corriger(req.mot)

@router.post("/correct/texte")
def correct_texte(req: TexteRequest):
    return {"resultats": verifier_texte(req.texte)}
