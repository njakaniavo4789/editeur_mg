"""
train.py
--------
Wires corpus.py → markov.py and produces a trained bigram.json.

Usage
-----
  python train.py                        # fetch Wikipedia + any local files
  python train.py --local-only           # only use local corpus/ folder
  python train.py --wiki-only            # only use Wikipedia
  python train.py --max-articles 100     # fetch more Wikipedia articles
  python train.py --model-path bi_gram/models/bigram.json

The script prints a quality report at the end so you know how good
the model is before shipping it.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------

# Broad Wikipedia search terms covering many Malagasy text domains
DEFAULT_WIKI_SEARCH = [
    "Madagasikara",        # general Madagascar
    "tantara",             # history
    "politika",            # politics
    "tontolo iainana",     # environment
    "fivavahana",          # religion / culture
    "siansa",              # science
    "fahasalamana",        # health
    "fambolena",           # agriculture
    "teny malagasy",       # language
    "geografy",            # geography
]


def quality_report(model, tokens: list[str]) -> None:
    """Print a simple quality report for the trained model."""
    from collections import Counter

    stats = model.stats()
    print("\n" + "=" * 55)
    print("  MODEL QUALITY REPORT")
    print("=" * 55)
    print(f"  Total tokens seen       : {stats['token_count']:,}")
    print(f"  Vocabulary size         : {stats['vocab_size']:,} unique words")
    print(f"  Total bigram pairs      : {stats['total_bigrams']:,}")

    avg_followers = (
        stats["total_bigrams"] / stats["vocab_size"]
        if stats["vocab_size"] else 0
    )
    print(f"  Avg followers per word  : {avg_followers:.1f}")

    # Coverage: % of vocab that has at least 2 different followers
    rich_words = sum(
        1 for followers in model.counts.values() if len(followers) >= 2
    )
    coverage = rich_words / stats["vocab_size"] * 100 if stats["vocab_size"] else 0
    print(f"  Words with ≥2 followers : {rich_words:,}  ({coverage:.1f}%)")

    # Top 10 most frequent words
    freq = Counter(tokens)
    print("\n  Top 10 most frequent words:")
    for word, count in freq.most_common(10):
        print(f"    {word:<20} {count:>6}")

    # Sample predictions for common Malagasy words
    sample_inputs = ["ny", "ny", "dia", "amin", "tany", "olona", "firenena", "ao"]
    seen_inputs = set()
    print("\n  Sample next-word predictions:")
    for w in sample_inputs:
        if w in seen_inputs or w not in model.counts:
            continue
        seen_inputs.add(w)
        preds = model.predict(w, top_n=3)
        preds_str = ", ".join(f"{p[0]} ({p[1]:.0%})" for p in preds)
        print(f"    '{w}' → {preds_str}")

    print("=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Train Malagasy bigram model")
    parser.add_argument("--local-only",    action="store_true",
                        help="Only use local corpus/ folder")
    parser.add_argument("--wiki-only",     action="store_true",
                        help="Only use Wikipedia MG")
    parser.add_argument("--local-dir",     default="corpus",
                        help="Path to local .txt corpus files (default: corpus/)")
    parser.add_argument("--model-path",    default="bi_gram/models/bigram.json",
                        help="Where to save the model (default: bi_gram/models/bigram.json)")
    parser.add_argument("--max-articles",  type=int, default=80,
                        help="Max Wikipedia articles to fetch (default: 80)")
    parser.add_argument("--force-retrain", action="store_true",
                        help="Retrain even if a saved model already exists")
    args = parser.parse_args()

    model_path = Path(args.model_path)

    # --- Skip retraining if model already exists ---
    if model_path.exists() and not args.force_retrain:
        logger.info("Model already exists at %s. Use --force-retrain to rebuild.", model_path)
        sys.exit(0)

    # --- Determine sources ---
    use_local = not args.wiki_only
    use_wiki  = not args.local_only

    # --- Load corpus ---
    from bi_gram.corpus import load_corpus
    from bi_gram.markov import BigramModel

    logger.info("Starting corpus collection…")
    tokens = load_corpus(
        local_dir=args.local_dir if use_local else None,
        wiki_search=DEFAULT_WIKI_SEARCH if use_wiki else None,
        wiki_max_articles=args.max_articles,
    )

    if len(tokens) < 100:
        logger.error(
            "Corpus too small (%d tokens). "
            "Add .txt files to '%s/' or increase --max-articles.",
            len(tokens), args.local_dir,
        )
        sys.exit(1)

    logger.info("Corpus ready: %d tokens", len(tokens))

    # --- Train ---
    logger.info("Training bigram model…")
    model = BigramModel()
    model.train(tokens)

    # --- Save ---
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)
    size_kb = model_path.stat().st_size / 1024
    logger.info("Model saved → %s (%.1f KB)", model_path, size_kb)

    # --- Quality report ---
    quality_report(model, tokens)


if __name__ == "__main__":
    main()