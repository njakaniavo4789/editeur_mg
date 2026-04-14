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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _suggest_remove(word: str, seq: str) -> str:
    """Remove the first occurrence of *seq* from *word*."""
    return word.replace(seq, "", 1)


def _suggest_replace(word: str, seq: str, replacement: str) -> str:
    return word.replace(seq, replacement, 1)


def _insert_vowel_after_cluster(word: str, cluster: str) -> str:
    """Insert 'a' between invalid start cluster and rest of word."""
    if len(word) > len(cluster):
        return word[:len(cluster)] + "a" + word[len(cluster):]
    return word


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
    # Combined pattern for better performance (single regex pass)
    _ALWAYS_FORBIDDEN_COMBINED = re.compile(r"(nb|mk|dt|bp|sz)")

    _FORBIDDEN_MAP = {
        "nb": ("FORBID_NB", "m", "nb"),
        "mk": ("FORBID_MK", "nk", "mk"),
        "dt": ("FORBID_DT", "t", "dt"),
        "bp": ("FORBID_BP", "mp", "bp"),
        "sz": ("FORBID_SZ", "s", "sz"),
    }

    def _forbidden_suggest(w, seq):
        repl = _FORBIDDEN_MAP[seq][1]
        return _suggest_replace(w, seq, repl)

    def _forbidden_match(text):
        m = _ALWAYS_FORBIDDEN_COMBINED.search(text)
        if m:
            seq = m.group()
            rule_id = _FORBIDDEN_MAP[seq][0]
            msg = f"La séquence '{seq}' n'existe pas en Malagasy."
            return rule_id, msg, seq
        return None

    rules.append({
        "id": "FORBID_COMBINED",
        "_match_fn": _forbidden_match,
        "suggest_fn": _forbidden_suggest,
    })

    # ------------------------------------------------------------------
    # 2.  Sequences forbidden at the START of a word
    # ------------------------------------------------------------------
    # TPML: Only tr, dr, ts, dz are valid start clusters in Malagasy
    # All others are invalid (including nk which is valid medially)
    # Exclude sequences already handled by FORBID_COMBINED (nb, mk, dt, bp, sz)
    _VALID_START_CLUSTERS = re.compile(r"^(tr|dr|ts|dz)")
    _ALWAYS_FORBIDDEN = ("nb", "mk", "dt", "bp", "sz")
    _INVALID_START_RE = re.compile(r"^([bcdfghjklmnpqrstvwxz]{2,})")

    def _start_cluster_match(text):
        m = _INVALID_START_RE.search(text)
        if m:
            cluster = m.group()
            if cluster in _ALWAYS_FORBIDDEN:
                return None
            if _VALID_START_CLUSTERS.match(cluster):
                return None
            return "FORBID_START_CLUSTER", f"La séquence '{cluster}' ne peut pas commencer un mot Malagasy.", cluster
        return None

    rules.append({
        "id": "FORBID_START_CLUSTER",
        "_match_fn": _start_cluster_match,
        "suggest_fn": lambda w, seq: _insert_vowel_after_cluster(w, seq),
    })

    # ------------------------------------------------------------------
    # 3.  Words must end in a vowel (a e i o y) or -na / -ny / -ka / -tra etc.
    # ------------------------------------------------------------------
    _END_CONSONANT_RE = re.compile(r"[bcdfghjklmnpqrstvwxz]$")

    def _end_consonant_match(text):
        m = _END_CONSONANT_RE.search(text)
        if m:
            return "END_CONSONANT", "Les mots Malagasy se terminent par une voyelle (a, e, i, o, u) ou -y.", m.group()
        return None

    rules.append({
        "id": "END_CONSONANT",
        "_match_fn": _end_consonant_match,
        "suggest_fn": lambda w, seq: w + "a",
    })

    # ------------------------------------------------------------------
    # 4.  Double consonants (gemination) – does not exist in Malagasy
    # ------------------------------------------------------------------
    _DOUBLE_CONSONANT_RE = re.compile(r"([bcdfghjklmnpqrstvwxz])\1")

    def _double_consonant_match(text):
        m = _DOUBLE_CONSONANT_RE.search(text)
        if m:
            seq = m.group()
            return "DOUBLE_CONSONANT", f"La consonne '{seq}' est doublée — la gémination n'existe pas en Malagasy.", seq
        return None

    rules.append({
        "id": "DOUBLE_CONSONANT",
        "_match_fn": _double_consonant_match,
        "suggest_fn": lambda w, seq: _suggest_replace(w, seq, seq[0]),
    })

    # ------------------------------------------------------------------
    # 5.  Three or more consonants in a row (very rare in Malagasy)
    # ------------------------------------------------------------------
    # Valid clusters: prenasalized stops (mp, mb, nd, ng, nj) + known digraphs
    _VALID_CLUSTERS = re.compile(
        r"^(nts|mts|ndr|mdr|ntr|mtr|str|tsr|ndz|mbr|mpr|nts)"
    )
    _PRENASALIZED = re.compile(r"(mp|mb|nd|ng|nj)")
    _TRIPLE_CONS_RE = re.compile(r"[bcdfghjklmnpqrstvwxz]{3,}")

    def _triple_match(text):
        m = _TRIPLE_CONS_RE.search(text)
        if m:
            seq = m.group()
            if _VALID_CLUSTERS.match(seq):
                return None
            if _PRENASALIZED.search(seq):
                return None
            return "TRIPLE_CONSONANT", f"Séquence de 3 consonnes ou plus '{seq}' — inhabituelle en Malagasy.", seq
        return None

    rules.append({
        "id": "TRIPLE_CONSONANT",
        "_match_fn": _triple_match,
        "suggest_fn": lambda w, seq: w,
    })

    return rules


RULES = _make_rules()

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
        match_fn = rule.get("_match_fn")
        if match_fn:
            result = match_fn(w_lower)
            if result:
                rule_id, msg, seq = result
                suggestion = rule["suggest_fn"](word, seq)
                errors.append({
                    "word":       word,
                    "sequence":   seq,
                    "rule_id":    rule_id,
                    "message":    msg,
                    "suggestion": suggestion,
                })

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
        ("trano",     False),   # valid - tr is valid cluster
        ("tantsaha",  False),   # valid
        ("tsara",     False),   # valid - ts is valid cluster
        ("mandeha",   False),   # valid
        ("hazo",      False),   # valid
        ("droa",      False),   # valid - dr is valid cluster
        ("dzaro",     False),   # valid - dz is valid cluster
        # --- should trigger errors ---
        ("nbola",     True),    # FORBID_NB
        ("mkasy",     True),    # FORBID_MK
        ("nkatra",    True),    # FORBID_START_CLUSTER (nk at start)
        ("szaka",     True),    # FORBID_SZ
        ("dtana",     True),    # FORBID_DT
        ("bpasy",     True),    # FORBID_BP
        ("zandrr",    True),    # DOUBLE_CONSONANT
        ("tanjom",    True),    # END_CONSONANT (ends in m)
        ("blato",     True),    # FORBID_START_CLUSTER (bl)
        ("pren",      True),    # FORBID_START_CLUSTER (pr)
        ("grilo",     True),    # FORBID_START_CLUSTER (gr)
        ("klio",     True),    # FORBID_START_CLUSTER (cl - french)
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