import re
import csv
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "../data/fototeny_sampateny_clean.csv")

PREFIXES = sorted([
    'mampifan', 'mampian', 'mampis', 'mampi', 'mamp',
    'mifan', 'mifampi', 'mian', 'maha', 'maham',
    'manampa', 'manam', 'manas', 'mana', 'man',
    'mpanao', 'mpanor', 'mpan', 'mpam', 'mpif',
    'mampan', 'mampi', 'mam', 'man',
    'miha', 'misy', 'mias', 'mise', 'mito', 'mits', 'mibo',
    'mi', 'ma', 'me',
    'fanampi', 'fanan', 'fanas', 'fana', 'fan', 'fam',
    'fiampi', 'fian', 'fias', 'fisa', 'fia',
    'faham', 'fahan', 'fahas', 'faha', 'fah',
    'aha', 'aha',
    'fan', 'fi', 'ha', 'ka',
], key=len, reverse=True)

SUFFIXES = sorted([
    'ana', 'ina', 'ena',
    'ahana', 'ahina', 'arana', 'arina',
    'araka', 'ariko', 'aretsika',
    'iana', 'enana', 'inana',
    'oana', 'avina', 'avina',
    'iana', 'ena',
], key=len, reverse=True)

INFIXES = ['in', 'om']

THEMATIC_CONSONANTS = ['v', 'z', 'f', 's', 'l', 'r', 'n', 't', 'd']


class AnalyseurMorphologique:
    def __init__(self):
        self.database = {}
        self._charger_database()

    def _charger_database(self):
        if not os.path.exists(CSV_PATH):
            logger.warning(f"CSV non trouvé : {CSV_PATH}")
            return
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fototeny = row.get('Fototeny', '').strip().lower()
                if not fototeny:
                    continue
                self.database[fototeny] = fototeny
                sampateny = row.get('sampateny', '')
                if sampateny:
                    for w in str(sampateny).split(','):
                        w = w.strip().lower().replace('"', '')
                        if w:
                            self.database[w] = fototeny
        logger.info(f"Base morphologique : {len(self.database)} entrées")

    def _decoupage_algo(self, word):
        word = word.lower()
        res = {"prefixe": "-", "infixe": "-", "suffixe": "-", "racine_algo": word}
        current = word

        for pref in PREFIXES:
            if current.startswith(pref) and len(current) > len(pref) + 2:
                res["prefixe"] = pref
                current = current[len(pref):]
                break

        for suff in SUFFIXES:
            if current.endswith(suff) and len(current) > len(suff) + 2:
                res["suffixe"] = suff
                current = current[:-len(suff)]
                if len(current) > 2 and current[-1] in THEMATIC_CONSONANTS:
                    current = current[:-1]
                break

        for inf in INFIXES:
            match = re.match(rf'^([^aeiouy]){inf}(.*)', current)
            if match:
                res["infixe"] = inf
                current = match.group(1) + match.group(2)
                break

        res["racine_algo"] = current
        return res

    def analyser(self, mot: str):
        mot = mot.strip().lower()
        analysis = self._decoupage_algo(mot)

        racine = analysis["racine_algo"]
        source = "Algorithme"

        if mot in self.database:
            racine = self.database[mot]
            source = "Base de données"

        return {
            "mot": mot,
            "prefixe": analysis["prefixe"],
            "infixe": analysis["infixe"],
            "suffixe": analysis["suffixe"],
            "lemme": racine,
            "source": source
        }


_analyseur = None

def get_analyseur():
    global _analyseur
    if _analyseur is None:
        _analyseur = AnalyseurMorphologique()
    return _analyseur


def lemmatiser(mot: str) -> str:
    return get_analyseur().analyser(mot)["lemme"]


def analyser_mot(mot: str):
    return get_analyseur().analyser(mot)
