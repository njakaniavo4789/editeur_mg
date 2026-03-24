from gtts import gTTS
import io

def generate_audio(text: str) -> bytes:
    """
    Prend un texte en malgache et retourne
    les octets (bytes) du fichier MP3 généré.
    """
    tts = gTTS(text=text, lang="fr")  # "mg" = malgache

    # On écrit le résultat en mémoire (pas sur le disque)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)

    return buffer.read()