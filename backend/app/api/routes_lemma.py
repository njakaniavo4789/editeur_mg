from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.lemmatiseur import lemmatiser

router = APIRouter()

class MotRequest(BaseModel):
    mot: str

@router.post("/lemma")
def lemma(req: MotRequest):
    return {"mot": req.mot, "racine": lemmatiser(req.mot)}
