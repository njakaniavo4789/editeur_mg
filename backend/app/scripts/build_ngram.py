"""
Script: build_ngram.py
Tanjona: Mampianatra N-gram model avy amin'ny corpus malagasy
Ampiasao: python -m app.scripts.build_ngram
"""
import os
from app.modules.ngram_model import construire_modele

CORPUS = os.path.join(os.path.dirname(__file__), "../../../data_raw/bible_mg.txt")

if __name__ == "__main__":
    if os.path.exists(CORPUS):
        print("Mampianatra modèle N-gram...")
        construire_modele(CORPUS)
        print("Vita! Modèle voatahiry.")
    else:
        print(f"Tsy hita ny corpus: {CORPUS}")
