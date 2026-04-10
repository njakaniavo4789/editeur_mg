"""
corpus.py
---------
Loads and normalises Malagasy text from two sources:
  1. Local .txt files in a given directory
  2. Wikipedia Malagasy API (mg.wikipedia.org)

Public API
----------
  load_corpus(local_dir=None, wiki_pages=None, wiki_search=None) -> list[str]
      Returns a flat list of normalised tokens.

  fetch_wikipedia_tokens(titles=None, search_terms=None, max_articles=50) -> list[str]
      Fetch and tokenise articles from mg.wikipedia.org.

  load_local_tokens(directory) -> list[str]
      Tokenise every .txt file found in *directory*.
"""

import re
import os
import time
import logging
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

# Malagasy uses the Latin alphabet. We lowercase and keep only
# Malagasy-valid characters: a-z plus common punctuation used as
# sentence boundaries.
_KEEP = re.compile(r"[a-z''-]+")   # apostrophe variants for contractions


def normalise(text: str) -> str:
    """Lowercase and strip non-alphabetic characters."""
    return text.lower()


def tokenise(text: str) -> list[str]:
    """
    Normalise *text* and return a list of word tokens.
    Empty strings and single-character tokens are discarded.
    """
    tokens = _KEEP.findall(normalise(text))
    return [t for t in tokens if len(t) > 1]


# ---------------------------------------------------------------------------
# Local file loader
# ---------------------------------------------------------------------------

def load_local_tokens(directory: str | Path) -> list[str]:
    """
    Read every *.txt file in *directory* (non-recursive) and return tokens.
    """
    directory = Path(directory)
    tokens: list[str] = []

    if not directory.exists():
        logger.warning("Local corpus directory not found: %s", directory)
        return tokens

    txt_files = list(directory.glob("*.txt"))
    if not txt_files:
        logger.warning("No .txt files found in %s", directory)
        return tokens

    for path in txt_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            file_tokens = tokenise(text)
            tokens.extend(file_tokens)
            logger.info("  Loaded %s → %d tokens", path.name, len(file_tokens))
        except Exception as exc:
            logger.error("  Failed to read %s: %s", path.name, exc)

    return tokens


# ---------------------------------------------------------------------------
# Wikipedia MG loader
# ---------------------------------------------------------------------------

_WIKI_API = "https://mg.wikipedia.org/w/api.php"
_HEADERS  = {"User-Agent": "MalagasyNLP-TP/1.0 (student project)"}
_DELAY    = 0.5   # seconds between requests (polite scraping)


def _wiki_get(params: dict) -> dict:
    """Low-level GET against the MediaWiki API."""
    params.setdefault("format", "json")
    params.setdefault("action", "query")
    resp = requests.get(_WIKI_API, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _fetch_article_text(title: str) -> Optional[str]:
    """Return the plain-text extract of a single article, or None on error."""
    try:
        data = _wiki_get({
            "prop":      "extracts",
            "explaintext": True,
            "titles":    title,
        })
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "missing" in page:
                logger.warning("  Wikipedia: article '%s' not found.", title)
                return None
            return page.get("extract", "")
    except Exception as exc:
        logger.error("  Wikipedia fetch error for '%s': %s", title, exc)
        return None


def _search_article_titles(term: str, limit: int = 10) -> list[str]:
    """Return up to *limit* article titles matching *term*."""
    try:
        data = _wiki_get({
            "list":     "search",
            "srsearch": term,
            "srlimit":  limit,
        })
        results = data.get("query", {}).get("search", [])
        return [r["title"] for r in results]
    except Exception as exc:
        logger.error("  Wikipedia search error for '%s': %s", term, exc)
        return []


def _get_random_titles(count: int = 20) -> list[str]:
    """Return *count* random article titles from mg.wikipedia.org."""
    try:
        data = _wiki_get({
            "list":          "random",
            "rnnamespace":   0,
            "rnlimit":       min(count, 500),
        })
        results = data.get("query", {}).get("random", [])
        return [r["title"] for r in results]
    except Exception as exc:
        logger.error("  Wikipedia random fetch error: %s", exc)
        return []


def fetch_wikipedia_tokens(
    titles: Optional[list[str]] = None,
    search_terms: Optional[list[str]] = None,
    max_articles: int = 50,
) -> list[str]:
    """
    Fetch Malagasy Wikipedia articles and return tokens.

    Parameters
    ----------
    titles       : explicit list of article titles to fetch
    search_terms : list of search keywords; top results are fetched
    max_articles : hard cap on total articles fetched
    """
    all_titles: list[str] = list(titles or [])

    # Resolve search terms to titles
    if search_terms:
        for term in search_terms:
            found = _search_article_titles(term, limit=5)
            all_titles.extend(found)
            time.sleep(_DELAY)

    # If nothing specified, grab random articles
    if not all_titles:
        logger.info("No titles specified — fetching random Wikipedia articles.")
        all_titles = _get_random_titles(count=max_articles)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_titles = []
    for t in all_titles:
        if t not in seen:
            seen.add(t)
            unique_titles.append(t)

    unique_titles = unique_titles[:max_articles]
    tokens: list[str] = []

    logger.info("Fetching %d Wikipedia articles…", len(unique_titles))
    for i, title in enumerate(unique_titles, 1):
        text = _fetch_article_text(title)
        if text:
            article_tokens = tokenise(text)
            tokens.extend(article_tokens)
            logger.info("  [%d/%d] '%s' → %d tokens (total: %d)",
                        i, len(unique_titles), title, len(article_tokens), len(tokens))
        time.sleep(_DELAY)

    return tokens


# ---------------------------------------------------------------------------
# Combined loader
# ---------------------------------------------------------------------------

def load_corpus(
    local_dir: Optional[str | Path] = None,
    wiki_titles: Optional[list[str]] = None,
    wiki_search: Optional[list[str]] = None,
    wiki_max_articles: int = 50,
) -> list[str]:
    """
    Load tokens from all available sources and return a combined list.

    Parameters
    ----------
    local_dir         : path to directory containing .txt corpus files
    wiki_titles       : explicit Wikipedia article titles to fetch
    wiki_search       : search terms used to find Wikipedia articles
    wiki_max_articles : max number of Wikipedia articles to fetch
    """
    tokens: list[str] = []

    if local_dir:
        logger.info("Loading local corpus from: %s", local_dir)
        local_tokens = load_local_tokens(local_dir)
        logger.info("Local corpus: %d tokens", len(local_tokens))
        tokens.extend(local_tokens)

    if wiki_titles or wiki_search or (not local_dir):
        logger.info("Loading Wikipedia MG corpus…")
        wiki_tokens = fetch_wikipedia_tokens(
            titles=wiki_titles,
            search_terms=wiki_search,
            max_articles=wiki_max_articles,
        )
        logger.info("Wikipedia corpus: %d tokens", len(wiki_tokens))
        tokens.extend(wiki_tokens)

    logger.info("Total corpus size: %d tokens", len(tokens))
    return tokens


# ---------------------------------------------------------------------------
# CLI usage:  python corpus.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    tokens = load_corpus(
        wiki_search=["Madagasikara", "tantara", "politika", "tontolo iainana"],
        wiki_max_articles=20,
    )
    print(f"\nTotal tokens collected: {len(tokens)}")
    print("Sample (first 30):", tokens[:30])
