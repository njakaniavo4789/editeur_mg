import re
import csv
import os

class MalagasyHybridAnalyzer:
    def __init__(self, affixes_file, csv_file):
        self.prefixes = []
        self.suffixes = []
        self.infixes = ['in', 'om']
        self.thematic_consonants = ['v', 'z', 'f', 's', 'l', 'r', 'n', 't', 'd']
        self.database = {} # {sampateny: fototeny}
        
        self.load_affixes(affixes_file)
        self.load_csv_database(csv_file)

    def load_affixes(self, filepath):
        """Charge les préfixes et suffixes depuis fanampiny.txt"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                # On trie par longueur décroissante pour matcher 'mampi' avant 'm'
                self.prefixes = sorted(re.findall(r'(\w+)~', content), key=len, reverse=True)
                self.suffixes = sorted(re.findall(r'~(\w+)', content), key=len, reverse=True)

    def load_csv_database(self, filepath):
        """Charge le dictionnaire de correspondance depuis le CSV"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    foto = row['Fototeny'].strip().lower()
                    if row['sampateny']:
                        for s in row['sampateny'].split(','):
                            s_clean = s.strip().lower().replace('"', '')
                            if s_clean:
                                self.database[s_clean] = foto
                    # La racine elle-même est dans la base
                    self.database[foto] = foto

    def algorithm_analysis(self, word):
        """Analyse structurelle (découpage)"""
        word = word.lower()
        res = {"p": "-", "i": "-", "s": "-", "root_algo": word}
        current = word

        # 1. Extraction du Préfixe
        for pref in self.prefixes:
            if current.startswith(pref):
                res["p"] = pref
                current = current[len(pref):]
                break

        # 2. Extraction du Suffixe
        for suff in self.suffixes:
            if current.endswith(suff):
                res["s"] = suff
                current = current[:-len(suff)]
                # Enlever la consonne thématique si elle existe (ex: 'v' dans 'tadiav')
                if len(current) > 2 and current[-1] in self.thematic_consonants:
                    current = current[:-1]
                break

        # 3. Extraction de l'Infixe
        for inf in self.infixes:
            match = re.match(rf'^([^aeiouy]){inf}(.*)', current)
            if match:
                res["i"] = inf
                current = match.group(1) + match.group(2)
                break

        res["root_algo"] = current
        return res

    def run(self, word):
        word = word.strip().lower()
        # Étape 1 : On fait le découpage algorithmique
        analysis = self.algorithm_analysis(word)
        
        # Étape 2 : On vérifie si le mot existe dans le CSV pour corriger la racine
        final_root = analysis["root_algo"]
        source = "Algorithme (Calculé)"
        
        if word in self.database:
            final_root = self.database[word]
            source = "CSV (Vérifié)"
        
        return {
            "orig": word,
            "p": analysis["p"],
            "i": analysis["i"],
            "s": analysis["s"],
            "root": final_root,
            "note": source
        }

# --- PROGRAMME PRINCIPAL ---
analyzer = MalagasyHybridAnalyzer("fanampiny.txt", "fototeny_sampateny_clean.csv")

print("="*90)
print(f"{'ANALYSEUR HYBRIDE : DÉCOUPAGE ALGO + VÉRIFICATION CSV':^90}")
print("="*90)

while True:
    input_word = input("\nEntrez un mot (ou 'q' pour quitter) : ").strip().lower()
    if input_word == 'q': break
    if not input_word: continue

    res = analyzer.run(input_word)

    print("\n" + "-"*95)
    print(f"{'Mot':<18} | {'Préfixe':<12} | {'Infixe':<8} | {'Suffixe':<8} | {'Racine (Final)':<15} | {'Source'}")
    print("-"*95)
    print(f"{res['orig']:<18} | {res['p']:<12} | {res['i']:<8} | {res['s']:<8} | {res['root']:<15} | {res['note']}")
    print("-"*95)