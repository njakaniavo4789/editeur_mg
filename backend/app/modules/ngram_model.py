import os, pickle
from collections import defaultdict
from nltk import ngrams, FreqDist

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../data/ngram_model.pkl")

def _charger_modele():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return defaultdict(FreqDist)

MODEL = _charger_modele()

def predire_mot_manaraka(mot: str, n: int = 3):
    mot = mot.lower()
    if mot in MODEL:
        return [w for w, _ in MODEL[mot].most_common(n)]
    return []

def construire_modele(corpus_path: str):
    with open(corpus_path, encoding="utf-8") as f:
        mots = f.read().lower().split()
    model = defaultdict(FreqDist)
    for w1, w2 in ngrams(mots, 2):
        model[w1][w2] += 1
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return model
