import pickle
import csv
import os
import logging
from rapidfuzz import process, utils
from app.modules.phonotactics_advanced import verifier_phonotactique_avance

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "../data/fototeny_sampateny_clean.csv")
CACHE_PATH = os.path.join(BASE_DIR, "../data/dictionnaire_cache.pkl")


class CorrecteurMalgache:
    def __init__(self):
        self.dictionnaire = []
        self.dictionnaire_set = set()
        self._charger_donnees()

    def _charger_donnees(self):
        if os.path.exists(CACHE_PATH):
            logger.info("Chargement du dictionnaire depuis le cache")
            with open(CACHE_PATH, 'rb') as f:
                self.dictionnaire = pickle.load(f)
        else:
            logger.info("Traitement du fichier CSV (première utilisation)")
            mots = set()
            if os.path.exists(CSV_PATH):
                with open(CSV_PATH, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        fototeny = row.get('Fototeny', '').strip()
                        if fototeny:
                            mots.add(fototeny.lower())
                        sampateny = row.get('sampateny', '')
                        if sampateny:
                            for w in str(sampateny).split(','):
                                w = w.strip().lower().replace('"', '')
                                if w:
                                    mots.add(w)
            self.dictionnaire = list(mots)
            with open(CACHE_PATH, 'wb') as f:
                pickle.dump(self.dictionnaire, f)

        self.dictionnaire_set = set(self.dictionnaire)
        logger.info(f"Dictionnaire prêt : {len(self.dictionnaire)} mots chargés")

    def corriger(self, mot_utilisateur: str, nb_suggestions: int = 5):
        mot = mot_utilisateur.lower().strip()

        if mot in self.dictionnaire_set:
            return {"mot": mot_utilisateur, "correct": True, "suggestions": []}

        suggestions = process.extract(
            mot,
            self.dictionnaire,
            limit=nb_suggestions,
            processor=utils.default_process
        )

        return {
            "mot": mot_utilisateur,
            "correct": False,
            "suggestions": [
                {"mot": s[0], "score": round(s[1], 2)}
                for s in suggestions if s[1] > 50
            ]
        }

    def verifier_texte(self, texte: str):
        resultats = []
        for mot in texte.split():
            clean = mot.strip(".,!?;:")
            if len(clean) < 2:
                continue
            correction = self.corriger(clean)
            phono_errors = verifier_phonotactique_avance(clean)
            has_phono = any(e.get("is_error", False) for e in phono_errors)
            if not correction["correct"] or has_phono:
                resultats.append({
                    "mot": clean,
                    "suggestions": [s["mot"] for s in correction["suggestions"]],
                    "scores": correction["suggestions"],
                    "erreurs_phonotactiques": phono_errors,
                })
        return resultats


_correcteur = None

def get_correcteur():
    global _correcteur
    if _correcteur is None:
        _correcteur = CorrecteurMalgache()
    return _correcteur


def corriger_mot(mot: str):
    c = get_correcteur().corriger(mot)
    if c["correct"]:
        return []
    return [s["mot"] for s in c["suggestions"]]


def verifier_texte(texte: str):
    return get_correcteur().verifier_texte(texte)
