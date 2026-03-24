from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

class TraductionRequest(BaseModel):
    mot: str
    source: str = "mg"
    cible: str = "fr"

@router.post("/translate")
def traduire(req: TraductionRequest):
    try:
        r = requests.post("https://libretranslate.com/translate", data={
            "q": req.mot, "source": req.source,
            "target": req.cible, "format": "text"
        }, timeout=5)
        traduction = r.json().get("translatedText", "Tsy hita")
    except Exception:
        traduction = "Erreur API"
    return {"mot": req.mot, "traduction": traduction}
