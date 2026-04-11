import pandas as pd

def traduire_mot_a_mot(phrase, chemin_csv):
    # 1. Charger le dictionnaire
    # On utilise sep=',' car ton fichier semble utiliser des virgules
    try:
        df = pd.read_csv(chemin_csv)
    except FileNotFoundError:
        return "Erreur : Le fichier dico2.csv est introuvable."

    # Nettoyage des données (enlever les espaces superflus)
    df['mot_malgache'] = df['mot_malgache'].str.strip().str.lower()
    df['resume_francais'] = df['resume_francais'].str.strip()

    # Création d'un dictionnaire Python pour une recherche rapide
    dico = dict(zip(df['mot_malgache'], df['resume_francais']))

    # 2. Traiter la phrase
    mots = phrase.lower().replace(',', '').replace('.', '').split()
    traduction = []

    for mot in mots:
        # On cherche le mot, si pas trouvé on garde le mot original entre crochets
        resultat = dico.get(mot, f"[{mot}]")
        traduction.append(resultat)

    return " ".join(traduction)

# --- Utilisation ---
fichier = 'dico2.csv'
ma_phrase = "tiko ny mihinana vary"  # Exemple de test

resultat = traduire_mot_a_mot(ma_phrase, fichier)

print(f"Phrase originale : {ma_phrase}")
print(f"Traduction mot à mot : {resultat}")