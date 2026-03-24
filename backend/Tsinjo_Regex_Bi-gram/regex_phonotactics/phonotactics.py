"""
phonotactics.py
---------------
Malagasy phonotactic rule checker.

Provides:
  - check_word(word)  -> list of ErrorResult
  - check_text(text)  -> list of ErrorResult  (one per offending word)

Each ErrorResult is a dict:
  {
    "word":       str,   # the original word that was checked
    "sequence":   str,   # the invalid sequence found inside the word
    "rule_id":    str,   # short identifier for the rule triggered
    "message":    str,   # human-readable explanation
    "suggestion": str,   # corrected / cleaned word (best-effort)
  }

Rules are derived from:
  - The TP annex  : nb, mk, nk (at start), dt, bp, sz anywhere
  - Malagasy phonology references:
      * No consonant cluster at word start except allowed ones
        (tr, dr, ts, dz are fine; others generally not)
      * Words must end in a vowel or -na / -ny / -nk is not allowed at end
      * Double consonants (gemination) do not exist in standard Malagasy
      * The sequences mp, mb, nd, ng, nj are legitimate prenasalised stops
        and should NOT be flagged
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _suggest_remove(word: str, seq: str) -> str:
    """Remove the first occurrence of *seq* from *word*."""
    return word.replace(seq, "", 1)


def _suggest_replace(word: str, seq: str, replacement: str) -> str:
    return word.replace(seq, replacement, 1)


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------
# Each rule is a dict:
#   id         : str          – short key
#   pattern    : re.Pattern   – compiled regex  (applied to lowercase word)
#   message    : str          – template; use {seq} for the matched sequence
#   suggest_fn : callable(word, match) -> str
#
# Rules are evaluated in order; ALL matching rules are reported (not just first).

def _make_rules():
    """Return the ordered list of phonotactic rule descriptors."""

    rules = []

    # ------------------------------------------------------------------
    # 1.  Sequences that are NEVER valid anywhere in a Malagasy word
    # ------------------------------------------------------------------
    always_forbidden = [
        # (regex_pattern, rule_id, friendly_name, replacement_hint)
        (r"nb",  "FORBID_NB",  "nb",  "m"),   # nb -> m  (labial assimilation)
        (r"mk",  "FORBID_MK",  "mk",  "nk"),  # mk -> nk
        (r"dt",  "FORBID_DT",  "dt",  "t"),   # dt -> t
        (r"bp",  "FORBID_BP",  "bp",  "mp"),  # bp -> mp
        (r"sz",  "FORBID_SZ",  "sz",  "s"),   # sz -> s
    ]

    for pat, rid, seq_name, repl in always_forbidden:
        _pat = pat          # capture for closure
        _rid = rid
        _repl = repl
        rules.append({
            "id": rid,
            "pattern": re.compile(pat),
            "message": f"La séquence '{seq_name}' n'existe pas en Malagasy.",
            "suggest_fn": lambda w, m, r=_repl, p=_pat: _suggest_replace(w, m.group(), r),
        })

    # ------------------------------------------------------------------
    # 2.  Sequences forbidden at the START of a word
    # ------------------------------------------------------------------
    # nk at word-start is forbidden (nk inside a word is a valid prenasalised stop)
    start_forbidden = [
        (r"^nk",  "FORBID_START_NK",  "nk",  "n"),
    ]

    for pat, rid, seq_name, repl in start_forbidden:
        _repl = repl
        rules.append({
            "id": rid,
            "pattern": re.compile(pat),
            "message": f"La séquence '{seq_name}' ne peut pas commencer un mot Malagasy.",
            "suggest_fn": lambda w, m, r=_repl: _suggest_replace(w, m.group(), r),
        })

    # ------------------------------------------------------------------
    # 3.  Words must end in a vowel (a e i o y) or -na / -ny / -ka / -tra etc.
    #     Ending in a plain consonant (other than -n) is non-Malagasy.
    # ------------------------------------------------------------------
    # Allowed final consonants after the main vowel check:
    #   -na, -ny are common suffixes → final 'a' or 'y' keeps it vowel-final already.
    #   In practice any word ending in a consonant that is NOT 'y' is suspicious.
    # We flag words ending in a consonant that is not 'y'.
    rules.append({
        "id": "END_CONSONANT",
        "pattern": re.compile(r"[bcdfghjklmnpqrstvwxz]$"),
        "message": "Les mots Malagasy se terminent par une voyelle (a, e, i, o, u) ou -y.",
        "suggest_fn": lambda w, m: w + "a",   # append 'a' as a generic hint
    })

    # ------------------------------------------------------------------
    # 4.  Double consonants (gemination) – does not exist in Malagasy
    # ------------------------------------------------------------------
    rules.append({
        "id": "DOUBLE_CONSONANT",
        "pattern": re.compile(r"([bcdfghjklmnpqrstvwxz])\1"),
        "message": "La consonne '{seq}' est doublée — la gémination n'existe pas en Malagasy.",
        "suggest_fn": lambda w, m: _suggest_replace(w, m.group(), m.group(1)),
    })

    # ------------------------------------------------------------------
    # 5.  Three or more consonants in a row (very rare in Malagasy)
    # ------------------------------------------------------------------
    # Known valid clusters in Malagasy (prenasalised stops + common digraphs):
    #   nts, mts, ndr, mdr, ntr, mtr, str, tsr, ndz, mbr, ndr
    # We only flag sequences NOT starting with one of those.
    _VALID_CLUSTERS = re.compile(
        r"^(nts|mts|ndr|mdr|ntr|mtr|str|tsr|ndz|mbr|mpr|nts)"
    )

    def _triple_suggest(w, m):
        return w  # no automatic fix

    def _triple_pattern_match(text):
        """Yield all 3+ consonant sequences that are NOT known-valid clusters."""
        for m in re.finditer(r"[bcdfghjklmnpqrstvwxz]{3,}", text):
            if not _VALID_CLUSTERS.match(m.group()):
                yield m

    # We store a custom finder instead of a plain pattern.
    rules.append({
        "id": "TRIPLE_CONSONANT",
        "pattern": None,                 # signals custom matching
        "_finder": _triple_pattern_match,
        "message": "Séquence de 3 consonnes ou plus '{seq}' — inhabituelle en Malagasy.",
        "suggest_fn": lambda w, m: w,
    })

    return rules


RULES = _make_rules()

# Vowels set (used for quick pre-filter)
_VOWELS = set("aeiouAEIOU")

# Tokeniser: split on whitespace and strip punctuation
_TOKEN_RE = re.compile(r"[^\s]+")
_PUNCT_STRIP = re.compile(r"^[^\w]+|[^\w]+$")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_word(word: str) -> list[dict]:
    """
    Check a single word against all phonotactic rules.

    Parameters
    ----------
    word : str
        A single token (no spaces).

    Returns
    -------
    list[dict]
        One dict per rule violation:
        {word, sequence, rule_id, message, suggestion}
    """
    errors = []
    w_lower = word.lower()

    for rule in RULES:
        finder = rule.get("_finder")
        matches = list(finder(w_lower)) if finder else list(rule["pattern"].finditer(w_lower))
        for match in matches:
            seq = match.group()
            suggestion = rule["suggest_fn"](word, match)
            msg = rule["message"].replace("{seq}", seq)
            errors.append({
                "word":       word,
                "sequence":   seq,
                "rule_id":    rule["id"],
                "message":    msg,
                "suggestion": suggestion,
            })
            break  # report each rule at most once per word

    return errors


def check_text(text: str) -> list[dict]:
    """
    Tokenise *text* and check every word.

    Returns a flat list of error dicts (same schema as check_word),
    deduplicated so the same (word, rule_id) pair is reported only once.
    """
    seen: set[tuple[str, str]] = set()
    errors: list[dict] = []

    for raw_token in _TOKEN_RE.findall(text):
        # Strip leading/trailing punctuation
        token = _PUNCT_STRIP.sub("", raw_token)
        if not token:
            continue

        for err in check_word(token):
            key = (err["word"].lower(), err["rule_id"])
            if key not in seen:
                seen.add(key)
                errors.append(err)

    return errors


# ---------------------------------------------------------------------------
# Flask/FastAPI integration helpers
# ---------------------------------------------------------------------------

def check_word_api(word: str) -> dict:
    """Wrap check_word for a JSON API endpoint."""
    return {
        "word": word,
        "valid": len(check_word(word)) == 0,
        "errors": check_word(word),
    }


def check_text_api(text: str) -> dict:
    """Wrap check_text for a JSON API endpoint."""
    errors = check_text(text)
    return {
        "error_count": len(errors),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Example Flask route (copy-paste into your app.py)
# ---------------------------------------------------------------------------
#
#   from flask import Flask, request, jsonify
#   from phonotactics import check_word_api, check_text_api
#
#   app = Flask(__name__)
#
#   @app.route("/check/word", methods=["GET"])
#   def api_check_word():
#       word = request.args.get("w", "")
#       return jsonify(check_word_api(word))
#
#   @app.route("/check/text", methods=["POST"])
#   def api_check_text():
#       body = request.get_json(force=True)
#       return jsonify(check_text_api(body.get("text", "")))
#
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Quick smoke-test  (python phonotactics.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = [
        # (word, expect_error)
        ("manosika",  False),   # valid
        ("tosika",    False),   # valid
        ("trano",     False),   # valid
        ("tantsaha",  False),   # valid
        ("tsara",     False),   # valid
        ("mandeha",   False),   # valid
        ("hazo",      False),   # valid
        # --- should trigger errors ---
        ("nbola",     True),    # FORBID_NB
        ("mkasy",     True),    # FORBID_MK
        ("nkatra",    True),    # FORBID_START_NK
        ("szaka",     True),    # FORBID_SZ
        ("dtana",     True),    # FORBID_DT
        ("bpasy",     True),    # FORBID_BP
        ("zandrr",    True),    # DOUBLE_CONSONANT
        ("tanjom",    True),    # END_CONSONANT (ends in m)
    ]

    print(f"{'Word':<15} {'Expected Error':<15} {'Got Error':<10} {'Details'}")
    print("-" * 70)
    for word, expect in test_cases:
        errs = check_word(word)
        got = len(errs) > 0
        status = "✓" if got == expect else "✗ MISMATCH"
        details = "; ".join(
            f"[{e['rule_id']}] seq='{e['sequence']}' → '{e['suggestion']}'"
            for e in errs
        ) or "—"
        print(f"{word:<15} {str(expect):<15} {str(got):<10} {status}  {details}")