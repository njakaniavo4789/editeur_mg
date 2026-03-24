from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.modules.tts_engine import generer_audio

router = APIRouter()

class TTSRequest(BaseModel):
    texte: str

@router.post("/tts")
async def tts(req: TTSRequest):
    path = await generer_audio(req.texte)
    return FileResponse(path, media_type="audio/mpeg", filename="output.mp3")
