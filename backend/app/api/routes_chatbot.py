from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
    # TODO: connecter Flowise ou LLM API
    return {"message": req.message, "reponse": "Chatbot ho avy..."}
