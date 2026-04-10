PREFIXES = ['mamp', 'mana', 'mam', 'man', 'maha', 'mpan', 'mpam', 'mi', 'ma', 'fi', 'fan', 'fam', 'ha']
SUFFIXES = ['ana', 'ina', 'na']

def lemmatiser(mot: str) -> str:
    mot = mot.lower()
    for pref in sorted(PREFIXES, key=len, reverse=True):
        if mot.startswith(pref) and len(mot) > len(pref) + 2:
            mot = mot[len(pref):]
            break
    for suf in sorted(SUFFIXES, key=len, reverse=True):
        if mot.endswith(suf) and len(mot) > len(suf) + 2:
            mot = mot[:-len(suf)]
            break
    return mot
