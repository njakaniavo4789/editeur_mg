from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from processor import MalagasyProcessor
from tts import generate_audio

app = FastAPI()
processor = MalagasyProcessor()


@app.get("/")
def root():
    return {"message": "API TTS Malagasy opérationnelle"}


@app.get("/speak")
async def speak(text: str, request: Request):
    # 1. Nettoyage du texte
    cleaned = processor.clean(text)

    if not cleaned:
        return JSONResponse(
            status_code=400,
            content={"error": "Texte vide après nettoyage"}
        )

    # 2. Génération audio
    audio_bytes = generate_audio(cleaned)
    total = len(audio_bytes)

    # 3. Gestion des range requests (pour les navigateurs)
    range_header = request.headers.get("Range")

    if range_header:
        range_val = range_header.strip().replace("bytes=", "")
        start_str, _, end_str = range_val.partition("-")
        start = int(start_str)
        end = int(end_str) if end_str else total - 1

        # Vérification que la plage est valide
        if start >= total or end >= total:
            return StreamingResponse(
                iter([]),
                status_code=416,
                headers={"Content-Range": f"bytes */{total}"}
            )

        chunk = audio_bytes[start:end + 1]
        return StreamingResponse(
            iter([chunk]),
            status_code=206,
            media_type="audio/mpeg",
            headers={
                "Content-Range": f"bytes {start}-{end}/{total}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(chunk)),
            }
        )

    # 4. Réponse normale (sans Range)
    return StreamingResponse(
        iter([audio_bytes]),
        status_code=200,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(total),
        }
    )