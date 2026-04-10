"""
markov.py
---------
Bigram Markov model for Malagasy next-word prediction.

Model structure (stored as JSON)
---------------------------------
{
  "word_a": {
    "word_b": 42,    ← raw count of "word_a word_b" in corpus
    "word_c": 17,
    ...
  },
  ...
}

Probabilities are computed on-the-fly from raw counts (no need to
store floats — saves space and allows easy merging of corpora).

Public API
----------
  BigramModel.train(tokens)               → fit on a token list
  BigramModel.save(path)                  → persist to JSON
  BigramModel.load(path)  [classmethod]   → restore from JSON
  BigramModel.predict(word, top_n=5)      → list of (word, probability) tuples
  BigramModel.predict_api(word, top_n=5)  → JSON-serialisable dict

  build_and_save(tokens, path)            → convenience one-liner
"""

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BigramModel:
    """Bigram (order-1 Markov) language model."""

    def __init__(self):
        # counts[w1][w2] = number of times w2 follows w1
        self.counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._token_count: int = 0

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, tokens: list[str]) -> "BigramModel":
        """
        Build bigram counts from a flat list of tokens.
        Can be called multiple times to accumulate counts (online learning).
        """
        if len(tokens) < 2:
            logger.warning("Token list too short to build bigrams (need ≥ 2).")
            return self

        for w1, w2 in zip(tokens, tokens[1:]):
            self.counts[w1][w2] += 1

        self._token_count += len(tokens)
        total_pairs = sum(sum(v.values()) for v in self.counts.values())
        logger.info("Model trained: %d unique first-words, %d bigram pairs",
                    len(self.counts), total_pairs)
        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, word: str, top_n: int = 5) -> list[tuple[str, float]]:
        """
        Return the *top_n* most likely words following *word*.

        Returns
        -------
        list of (next_word, probability) sorted by probability descending.
        Empty list if *word* was never seen in training data.
        """
        word = word.lower().strip()
        followers = self.counts.get(word)

        if not followers:
            # Fallback: return the globally most frequent words
            return self._global_top(top_n)

        total = sum(followers.values())
        ranked = sorted(followers.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [(w, count / total) for w, count in ranked]

    def _global_top(self, top_n: int) -> list[tuple[str, float]]:
        """Return the most frequent words overall (used as fallback)."""
        freq: dict[str, int] = defaultdict(int)
        for followers in self.counts.values():
            for w, c in followers.items():
                freq[w] += c
        total = sum(freq.values()) or 1
        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [(w, c / total) for w, c in ranked]

    def predict_api(self, word: str, top_n: int = 5) -> dict:
        """
        Wrap predict() for a JSON API response.

        Returns
        -------
        {
          "input":       "tanana",
          "suggestions": [
            {"word": "lehibe", "probability": 0.312},
            ...
          ],
          "fallback": false   ← true when input word was unseen
        }
        """
        word_clean = word.lower().strip()
        is_fallback = word_clean not in self.counts
        predictions = self.predict(word_clean, top_n=top_n)
        return {
            "input": word,
            "suggestions": [
                {"word": w, "probability": round(p, 4)}
                for w, p in predictions
            ],
            "fallback": is_fallback,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Serialise model to a human-readable JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert defaultdicts to plain dicts for JSON serialisation
        data = {
            "meta": {
                "type":        "bigram",
                "token_count": self._token_count,
                "vocab_size":  len(self.counts),
            },
            "counts": {w1: dict(w2s) for w1, w2s in self.counts.items()},
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        size_kb = path.stat().st_size / 1024
        logger.info("Model saved to %s (%.1f KB)", path, size_kb)

    @classmethod
    def load(cls, path: str | Path) -> "BigramModel":
        """
        Load a model previously saved with save().
        Raises FileNotFoundError if the file does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        model = cls()
        raw_counts = data.get("counts", {})

        for w1, w2s in raw_counts.items():
            for w2, c in w2s.items():
                model.counts[w1][w2] = c

        meta = data.get("meta", {})
        model._token_count = meta.get("token_count", 0)

        logger.info(
            "Model loaded from %s — vocab: %d words, tokens seen: %d",
            path, len(model.counts), model._token_count,
        )
        return model

    # ------------------------------------------------------------------
    # Stats / debug
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        total_pairs = sum(sum(v.values()) for v in self.counts.values())
        return {
            "vocab_size":   len(self.counts),
            "total_bigrams": total_pairs,
            "token_count":  self._token_count,
        }


# ---------------------------------------------------------------------------
# Convenience one-liner
# ---------------------------------------------------------------------------

def build_and_save(tokens: list[str], path: str | Path) -> BigramModel:
    """Train a fresh model on *tokens* and immediately persist it."""
    model = BigramModel()
    model.train(tokens)
    model.save(path)
    return model


def load_or_build(
    model_path: str | Path,
    tokens_fn,           # callable() -> list[str], used only if model absent
) -> BigramModel:
    """
    Load the model from *model_path* if it exists.
    Otherwise call *tokens_fn()* to get tokens, build, save, and return.

    Usage
    -----
        model = load_or_build(
            "bi_gram/models/bigram.json",
            tokens_fn=lambda: load_corpus(local_dir="corpus/", wiki_search=["Madagasikara"]),
        )
    """
    model_path = Path(model_path)
    if model_path.exists():
        return BigramModel.load(model_path)

    logger.info("No saved model found at %s — building from scratch…", model_path)
    tokens = tokens_fn()
    return build_and_save(tokens, model_path)


# ---------------------------------------------------------------------------
# Flask/FastAPI integration snippet
# ---------------------------------------------------------------------------
#
#   from flask import Flask, request, jsonify
#   from markov import load_or_build
#   from corpus import load_corpus
#
#   app = Flask(__name__)
#
#   MODEL = load_or_build(
#       model_path="bi_gram/models/bigram.json",
#       tokens_fn=lambda: load_corpus(
#           local_dir="corpus/",
#           wiki_search=["Madagasikara", "tantara", "politika"],
#           wiki_max_articles=50,
#       ),
#   )
#
#   @app.route("/predict")
#   def api_predict():
#       word  = request.args.get("w", "")
#       top_n = int(request.args.get("n", 5))
#       return jsonify(MODEL.predict_api(word, top_n=top_n))
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Smoke test  (python markov.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    import tempfile, os

    # --- tiny synthetic corpus ---
    # sample_text = """
    # ny tanana lehibe ao Madagasikara dia Antananarivo
    # ny tanana kely dia maro be
    # ny olona ao amin ny tanana lehibe dia maro
    # ny firenena malagasy dia Madagasikara
    # ny tany malagasy dia tsara
    # ny olona malagasy dia hendry
    # ny firenena lehibe dia maro amin izao tontolo izao
    # """

    # from corpus import tokenise
    # tokens = tokenise(sample_text)
    # print(f"Sample tokens ({len(tokens)}): {tokens[:15]} …\n")

    # model = BigramModel()
    # model.train(tokens)

    # print("Stats:", model.stats())
    # print()

    # Use the trained model from md/wikipedia
    # Corpus.py actually used

    # -----------------------------------------------
    # Load the trained model
    model = BigramModel.load("bi_gram/models/bigram.json")

    # Predict next word
    predictions = model.predict("ny", top_n=5)
    for word, prob in predictions:
        print(f"{word}: {prob:.1%}")

        # Test predictions
        test_words = ["ny", "tanana", "olona", "tany", "unknownword"]
        for w in test_words:
            result = model.predict_api(w, top_n=3)
            print(f"  predict('{w}') → {result}")

    # -----------------------------------------------
    # Save / reload round-trip
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp_path = f.name

    model.save(tmp_path)
    model2 = BigramModel.load(tmp_path)
    os.unlink(tmp_path)

    assert model2.predict("ny", top_n=1) == model.predict("ny", top_n=1), \
        "Round-trip mismatch!"
    print("\n✓ Save/load round-trip OK")
