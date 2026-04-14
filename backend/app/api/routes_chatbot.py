from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.chatbot_gemini import envoyer_message, reset_session

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

class ChatResetRequest(BaseModel):
    user_id: str = "default"

@router.post("/chat")
def chat(req: ChatRequest):
    reponse = envoyer_message(req.message, req.user_id)
    return {"message": req.message, "reponse": reponse}

@router.post("/chat/reset")
def chat_reset(req: ChatResetRequest):
    reset_session(req.user_id)
    return {"status": "ok", "message": "Sarin-dresaka vaovao"}
