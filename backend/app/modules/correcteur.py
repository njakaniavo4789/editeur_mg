import json, os
from rapidfuzz import process, fuzz
from app.modules.phonotactique import verifier_phonotactique
from app.modules.phonotactics_advanced import verifier_phonotactique_avance, check_word

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/dictionnaire_mg.json")

def _charger_dictionnaire():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, encoding="utf-8") as f:
            return list(json.load(f).keys())
    return []

DICTIONNAIRE = _charger_dictionnaire()

def corriger_mot(mot: str):
    """Find spelling suggestions for a word using fuzzy matching."""
    if mot in DICTIONNAIRE:
        return []
    resultats = process.extract(mot, DICTIONNAIRE, scorer=fuzz.ratio, limit=5)
    return [r[0] for r in resultats if r[1] > 60]

def corriger_mot_avance(mot: str):
    """Advanced correction: spelling + phonotactics."""
    # Basic fuzzy suggestions
    suggestions = corriger_mot(mot)
    
    # Advanced phonotactics check
    phono_errors = verifier_phonotactique_avance(mot)
    has_phono_error = any(e.get("is_error", False) for e in phono_errors)
    
    return {
        "mot": mot,
        "suggestions": suggestions,
        "erreurs_phonotactiques": phono_errors,
        "est_valide": len(phono_errors) == 0 and len(suggestions) == 0,
    }

def verifier_texte(texte: str):
    """Verify full text - basic version."""
    mots = texte.split()
    resultats = []
    for mot in mots:
        erreur_phono = verifier_phonotactique(mot)
        suggestions = corriger_mot(mot)
        if erreur_phono or suggestions:
            resultats.append({
                "mot": mot,
                "erreur_phonotactique": erreur_phono,
                "suggestions": suggestions
            })
    return resultats

def verifier_texte_avance(texte: str):
    """Verify full text - advanced version with detailed phonotactics."""
    mots = texte.split()
    resultats = []
    for mot in mots:
        if len(mot) > 1:
            phono_errors = verifier_phonotactique_avance(mot)
            suggestions = corriger_mot(mot)
            has_error = any(e.get("is_error", False) for e in phono_errors)
            if has_error or suggestions:
                resultats.append({
                    "mot": mot,
                    "erreurs_phonotactiques": phono_errors,
                    "suggestions": suggestions
                })
    return resultats
