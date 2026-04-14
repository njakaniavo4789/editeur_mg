from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.bigram_model import predire_mot_manaraka, predire_mot_manaraka_advanced

router = APIRouter()

class CompleteRequest(BaseModel):
    mot: str
    n: int = 3

@router.post("/complete")
def autocomplete(req: CompleteRequest):
    """Simple autocomplete - returns list of words."""
    return {"mot": req.mot, "suggestions": predire_mot_manaraka(req.mot, req.n)}

@router.post("/complete/advanced")
def autocomplete_advanced(req: CompleteRequest):
    """Advanced autocomplete - returns words with probabilities."""
    return predire_mot_manaraka_advanced(req.mot, req.n)
