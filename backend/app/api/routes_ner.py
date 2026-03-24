from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.ner import detecter_entites

router = APIRouter()

class TexteRequest(BaseModel):
    texte: str

@router.post("/ner")
def ner(req: TexteRequest):
    return {"texte": req.texte, "entites": detecter_entites(req.texte)}
