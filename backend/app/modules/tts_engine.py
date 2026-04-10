import edge_tts
import tempfile, os

async def generer_audio(texte: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.close()
    tts = edge_tts.Communicate(texte, voice="mg-MG-VahinyNeural")
    await tts.save(tmp.name)
    return tmp.name
