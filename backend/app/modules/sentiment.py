import os

def _charger_liste(filename):
    path = os.path.join(os.path.dirname(__file__), f"../data/{filename}")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()

POSITIF = _charger_liste("sentiment_positif.txt")
NEGATIF = _charger_liste("sentiment_negatif.txt")

def analyser_sentiment(texte: str):
    mots = texte.lower().split()
    score = sum(1 for m in mots if m in POSITIF) - sum(1 for m in mots if m in NEGATIF)
    if score > 0: return {"label": "POSITIF", "score": score}
    if score < 0: return {"label": "NEGATIF", "score": score}
    return {"label": "NEUTRE", "score": 0}
