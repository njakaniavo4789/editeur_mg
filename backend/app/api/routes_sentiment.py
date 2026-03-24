from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.sentiment import analyser_sentiment

router = APIRouter()

class TexteRequest(BaseModel):
    texte: str

@router.post("/sentiment")
def sentiment(req: TexteRequest):
    return {"texte": req.texte, "resultat": analyser_sentiment(req.texte)}
