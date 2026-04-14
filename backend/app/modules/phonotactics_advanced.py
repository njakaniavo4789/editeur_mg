"""
phonotactics_advanced.py
-----------------------
Advanced phonotactic rule checker for Malagasy.
Based on Tsinjo's regex_phonotactics module.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _suggest_remove(word: str, seq: str) -> str:
    """Remove the first occurrence of *seq* from *word*."""
    return word.replace(seq, "", 1)


def _suggest_replace(word: str, seq: str, replacement: str) -> str:
    return word.replace(seq, replacement, 1)


# Valid consonant clusters in Malagasy
_VALID_CLUSTERS = re.compile(
    r"^(nts|mts|ndr|mdr|ntr|mtr|str|tsr|ndz|mbr|mpr)"
)


# ----------------------------------------------------------------------
# Rule definitions
# ----------------------------------------------------------------------
RULES = []

# 1. Sequences NEVER valid anywhere in Malagasy
forbidden_always = [
    (r"nb", "nb -> m (labial assimilation)"),
    (r"mk", "mk -> nk"),
    (r"dt", "dt -> t"),
    (r"bp", "bp -> mp"),
    (r"sz", "sz -> s"),
]
for pat, suggestion in forbidden_always:
    RULES.append({
        "id": f"FORBID_{pat.upper()}",
        "pattern": re.compile(pat, re.IGNORECASE),
        "message": f"La séquence '{pat}' n'existe pas en Malagasy.",
        "suggestion": suggestion,
        "is_error": True,
    })

# 2. Forbidden at word START only
start_forbidden = [
    (r"^nk", "nk -> n (début de mot)"),
]
for pat, suggestion in start_forbidden:
    RULES.append({
        "id": "FORBID_START_NK",
        "pattern": re.compile(pat, re.IGNORECASE),
        "message": "nk ne peut pas commencer un mot Malagasy.",
        "suggestion": suggestion,
        "is_error": True,
    })

# 3. Double consonants (gemination) - does not exist in Malagasy
RULES.append({
    "id": "DOUBLE_CONSONANT",
    "pattern": re.compile(r"([bcdfghjklmnpqrstvwxz])\1", re.IGNORECASE),
    "message": "La consonne '{seq}' est doublée — la gémination n'existe pas en Malagasy.",
    "suggestion": "Retirer la consonne doublée",
    "is_error": True,
})

# 4. Three or more consonants in a row
def find_triple_consonants(word):
    """Find 3+ consonant sequences that are NOT valid clusters."""
    results = []
    for m in re.finditer(r"[bcdfghjklmnpqrstvwxz]{3,}", word, re.IGNORECASE):
        if not _VALID_CLUSTERS.match(m.group()):
            results.append(m.group())
    return results


def check_word(word: str) -> list:
    """
    Check a single word for phonotactic errors.
    
    Returns list of ErrorResult:
    {
        "word": str,
        "sequence": str,
        "rule_id": str,
        "message": str,
        "suggestion": str,
        "is_error": bool
    }
    """
    word_lower = word.lower()
    errors = []
    
    for rule in RULES:
        match = rule["pattern"].search(word_lower)
        if match:
            errors.append({
                "word": word,
                "sequence": match.group(),
                "rule_id": rule["id"],
                "message": rule["message"].format(seq=match.group()),
                "suggestion": rule["suggestion"],
                "is_error": rule["is_error"],
            })
    
    # Check triple consonants
    triple = find_triple_consonants(word_lower)
    for seq in triple:
        errors.append({
            "word": word,
            "sequence": seq,
            "rule_id": "TRIPLE_CONSONANT",
            "message": f"La séquence '{seq}' de 3 consonnes consécutives est rare en Malagasy.",
            "suggestion": "Vérifiez l'orthographe",
            "is_error": False,
        })
    
    return errors


def check_text(text: str) -> list:
    """
    Check a full text for phonotactic errors.
    
    Returns list of ErrorResult for each offending word.
    """
    # Split into words (roughly)
    words = text.split()
    all_errors = []
    
    for word in words:
        # Clean punctuation
        clean_word = re.sub(r'[.,!?;:()"\']', '', word)
        if clean_word and clean_word.isalpha() and len(clean_word) > 1:
            errors = check_word(clean_word)
            all_errors.extend(errors)
    
    return all_errors


def verifier_phonotactique_avance(mot: str) -> list:
    """API function: verify phonotactics of a word."""
    return check_word(mot)


def verifier_phrase_avance(phrase: str) -> list:
    """API function: verify phonotactics of a full text."""
    return check_text(phrase)