from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.lemmatiseur import lemmatiser, analyser_mot

router = APIRouter()

class MotRequest(BaseModel):
    mot: str

@router.post("/lemma")
def lemma(req: MotRequest):
    return {"mot": req.mot, "lemme": lemmatiser(req.mot)}

@router.post("/lemma/analyse")
def lemma_analyse(req: MotRequest):
    return analyser_mot(req.mot)
