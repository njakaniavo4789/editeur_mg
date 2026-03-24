import re

FORBIDDEN_PATTERNS = [
    (r'\bnb', "nb eo am-piandohana"),
    (r'\bmk', "mk eo am-piandohana"),
    (r'\bnk', "nk eo am-piandohana"),
    (r'dt',   "dt tsy misy"),
    (r'bp',   "bp tsy misy"),
    (r'sz',   "sz tsy misy"),
]

def verifier_phonotactique(mot: str):
    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, mot, re.IGNORECASE):
            return message
    return None
