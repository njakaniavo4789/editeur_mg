import pandas as pd
import pickle
import os
from rapidfuzz import process, utils

class CorrecteurMalgache:
    def __init__(self, csv_path, cache_path='dictionnaire.pkl'):
        self.csv_path = csv_path
        self.cache_path = cache_path
        self.dictionnaire = []
        self.dictionnaire_set = set()
        
        # Charger ou créer le dictionnaire
        self._charger_donnees()

    def _charger_donnees(self):
        """Charge le cache s'il existe, sinon traite le CSV."""
        if os.path.exists(self.cache_path):
            print(f"--- Chargement du dictionnaire depuis le cache ({self.cache_path}) ---")
            with open(self.cache_path, 'rb') as f:
                self.dictionnaire = pickle.load(f)
        else:
            print("--- Traitement du fichier CSV (première utilisation) ---")
            df = pd.read_csv(self.csv_path)
            mots = set()
            
            # Ajouter les racines (Fototeny)
            mots.update(df['Fototeny'].dropna().astype(str).tolist())
            
            # Ajouter les dérivés (sampateny)
            for derivees in df['sampateny'].dropna():
                liste_mots = [w.strip() for w in str(derivees).split(',')]
                mots.update(liste_mots)
            
            self.dictionnaire = list(mots)
            
            # Sauvegarder pour la prochaine fois
            with open(self.cache_path, 'wb') as f:
                pickle.dump(self.dictionnaire, f)
        
        # Créer un set pour une recherche exacte ultra-rapide
        self.dictionnaire_set = set(self.dictionnaire)
        print(f"Dictionnaire prêt : {len(self.dictionnaire)} mots chargés.")

    def corriger(self, mot_utilisateur, nb_suggestions=3):
        """Vérifie le mot et propose des corrections si nécessaire."""
        mot = mot_utilisateur.lower().strip()
        
        # 1. Vérification exacte (Table de hachage)
        if mot in self.dictionnaire_set:
            return f"'{mot_utilisateur}' est correct !"

        # 2. Recherche de proximité (Levenshtein via RapidFuzz)
        print(f"'{mot_utilisateur}' non trouvé. Recherche de suggestions...")
        suggestions = process.extract(
            mot, 
            self.dictionnaire, 
            limit=nb_suggestions,
            processor=utils.default_process
        )
        
        return suggestions

# --- EXEMPLE D'UTILISATION ---
if __name__ == "__main__":
    # Assurez-vous que le fichier est au bon endroit
    correcteur = CorrecteurMalgache('fototeny_sampateny_clean.csv')

    while True:
        test = input("\nEntrez un mot malgache (ou 'q' pour quitter) : ")
        if test.lower() == 'q':
            break
            
        resultat = correcteur.corriger(test)
        
        if isinstance(resultat, str):
            print(resultat)
        else:
            print("Suggestions :")
            for res in resultat:
                # res[0] = mot, res[1] = score, res[2] = index
                print(f" - {res[0]} (score: {round(res[1], 2)})")