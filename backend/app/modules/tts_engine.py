import torch
import scipy.io.wavfile
import tempfile
import os
import numpy as np

from transformers import VitsModel, AutoTokenizer

MODEL_ID = "facebook/mms-tts-mlg"
_model = None
_tokenizer = None


def load_model():
    global _model, _tokenizer
    if _model is None:
        print("[TTS] Chargement du modèle facebook/mms-tts-mlg...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _model = VitsModel.from_pretrained(MODEL_ID)
        _model.eval()
        print("[TTS] Modèle chargé avec succès")
    return _model, _tokenizer


def preprocess_malagasy(text: str) -> str:
    text = text.strip().lower()
    text = text.replace('–', '-').replace('—', '-')
    allowed_extras = set("àâäéèêëîïôùûü-.,!?;:' ")
    cleaned = ''.join(c for c in text if c.isalpha() or c.isdigit() or c in allowed_extras)
    cleaned = ' '.join(cleaned.split())
    return cleaned


def normalize_audio(waveform: np.ndarray) -> np.ndarray:
    max_val = np.abs(waveform).max()
    if max_val > 0:
        waveform = waveform / max_val * 0.95
    return waveform


async def generer_audio(texte: str) -> str:
    model, tokenizer = load_model()

    texte_clean = preprocess_malagasy(texte)
    inputs = tokenizer(texte_clean, return_tensors="pt")

    with torch.no_grad():
        torch.manual_seed(42)
        output = model(**inputs)

    waveform = output.waveform.squeeze().cpu().numpy()
    sample_rate = model.config.sampling_rate

    waveform = normalize_audio(waveform)
    waveform_int = (waveform * 32767).astype(np.int16)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()
    scipy.io.wavfile.write(tmp.name, sample_rate, waveform_int)
    return tmp.name