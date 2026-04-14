"""
bigram_model.py
-------------
Wrapper around Tsinjo's Markov Bigram model for next-word prediction.
"""

import os
import json
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "Tsinjo_Regex_Bi-gram" / "bi_gram" / "models" / "bigram.json"
CORPUS_PATH = BASE_DIR / "data_raw" / "corpus_mg.txt"


class BigramPredictor:
    """Wrapper for Markov Bigram model."""
    
    def __init__(self):
        self.counts = defaultdict(lambda: defaultdict(int))
        self._token_count = 0
        self._loaded = False
    
    def _ensure_loaded(self):
        """Lazy load the model."""
        if self._loaded:
            return
        
        # Try to load existing model
        if MODEL_PATH.exists():
            try:
                with open(MODEL_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                raw_counts = data.get("counts", {})
                for w1, w2s in raw_counts.items():
                    for w2, c in w2s.items():
                        self.counts[w1][w2] = c
                
                meta = data.get("meta", {})
                self._token_count = meta.get("token_count", 0)
                logger.info(f"Loaded bigram model from {MODEL_PATH}")
                self._loaded = True
                return
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
        
        # If no model, create simple fallback model
        logger.info("Creating fallback bigram model...")
        self._create_fallback_model()
        self._loaded = True
    
    def _create_fallback_model(self):
        """Create a simple fallback model with common Malagasy word patterns."""
        # Common Malagasy word pairs
        common_pairs = {
            "ny": {"rahalah": 0.3, "olona": 0.2, "ankizy": 0.15, "tany": 0.1, "fianarana": 0.1},
            "a": {"iza": 0.2, "izao": 0.15, "ianao": 0.1, "hy": 0.1, "mety": 0.05},
            "manana": {"fahasahiana": 0.2, "fahavonona": 0.15, "tantara": 0.1, "laza": 0.1},
            "miteny": {"amy": 0.2, "amin": 0.15, "izany": 0.1, "io": 0.1, "roa": 0.05},
            "manda": {"osa": 0.2, "nanto": 0.15, "nitera": 0.1, "fitsike": 0.1},
            "raha": {"mba": 0.2, "izao": 0.15, "mbo": 0.1, "ni": 0.1, "dia": 0.05},
            "teny": {"malagasy": 0.2, "madagascar": 0.15, "noforonina": 0.1, "vaovao": 0.1},
            "fahal": {"anahana": 0.2, "anana": 0.15, "azana": 0.1, "arana": 0.1},
            "fahafahana": {"hanatanteraka": 0.2, "hifanatrehana": 0.15, "hifankahala": 0.1},
            "haseh": {"o": 0.2, "ana": 0.15, "an": 0.1, "iko": 0.1, "ikoa": 0.05},
        }
        for w1, words in common_pairs.items():
            for w2, count in words.items():
                self.counts[w1][w2] = int(count * 100)
        
        self._token_count = sum(sum(d.values()) for d in self.counts.values())
    
    def predict(self, word: str, top_n: int = 5):
        """Predict next words after *word*."""
        self._ensure_loaded()
        
        word = word.lower().strip()
        followers = self.counts.get(word)
        
        if not followers:
            return [w for w, _ in sorted(
                {w2: c for w1, w2s in self.counts.items() for w2, c in w2s.items()}.items(),
                key=lambda x: x[1], reverse=True
            )[:top_n]]
        
        total = sum(followers.values())
        ranked = sorted(followers.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [w for w, _ in ranked]
    
    def predict_with_probs(self, word: str, top_n: int = 5):
        """Predict next words with probabilities."""
        self._ensure_loaded()
        
        word = word.lower().strip()
        followers = self.counts.get(word)
        
        if not followers:
            # Return fallback
            freq = defaultdict(int)
            for w1, w2s in self.counts.values():
                for w2, c in w2s.items():
                    freq[w2] += c
            
            total = sum(freq.values()) or 1
            ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
            return {"input": word, "suggestions": [{"word": w, "probability": round(c/total, 4)} for w, c in ranked], "fallback": True}
        
        total = sum(followers.values())
        ranked = sorted(followers.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return {
            "input": word,
            "suggestions": [{"word": w, "probability": round(c/total, 4)} for w, c in ranked],
            "fallback": False
        }


# Singleton instance
_model = None

def get_model():
    global _model
    if _model is None:
        _model = BigramPredictor()
    return _model


def predire_mot_manaraka(mot: str, n: int = 5):
    """API function: predict next words."""
    model = get_model()
    return model.predict(mot, n)


def predire_mot_manaraka_advanced(mot: str, n: int = 5):
    """API function: predict next words with probabilities."""
    model = get_model()
    return model.predict_with_probs(mot, n)