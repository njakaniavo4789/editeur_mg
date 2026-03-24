from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.ngram_model import predire_mot_manaraka

router = APIRouter()

class CompleteRequest(BaseModel):
    mot: str
    n: int = 3

@router.post("/complete")
def autocomplete(req: CompleteRequest):
    return {"mot": req.mot, "suggestions": predire_mot_manaraka(req.mot, req.n)}
