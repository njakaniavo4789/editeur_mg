# -*- coding: utf-8 -*-
"""
🎤 SYNTHÈSE VOCALE MALGACHE - Version 2.0 améliorée
Accent malgache réaliste via :
  1. Phonétique malgache rigoureuse (accent, syllabes, consonnes finales, etc.)
  2. Post-traitement audio avec pydub (pitch, tempo, EQ, réverbération)

Dépendances :
    pip install gtts pydub pygame
    # + ffmpeg dans le PATH (https://ffmpeg.org/download.html)
"""

import re
import time
import os
from gtts import gTTS

# ── Imports optionnels ────────────────────────────────────────────────
try:
    from pydub import AudioSegment
    from pydub.effects import normalize, low_pass_filter
    PYDUB_OK = True
except ImportError:
    PYDUB_OK = False
    print("⚠️  pydub non installé → post-traitement audio désactivé")
    print("   Installez : pip install pydub  +  ffmpeg dans votre PATH")

try:
    import pygame
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False

# ─────────────────────────────────────────────────────────────────────
# PARTIE 1 : PHONÉTIQUE MALGACHE
# ─────────────────────────────────────────────────────────────────────

# Groupes consonantiques malgaches → prononciation française approchée
CONSONNES_MG = {
    # Géminées et clusters typiques
    "ts":  "ts",
    "tr":  "tr",
    "dr":  "dr",
    "mb":  "mb",
    "mp":  "mp",
    "nd":  "nd",
    "ng":  "ng",
    "nk":  "nk",
    "nt":  "nt",
    "nts": "nts",
    "ny":  "gni",   # ny malgache → son "gn" français
    "ry":  "ri",
    "ty":  "tchi",
    "dy":  "dji",
    "ky":  "ki",
    "vy":  "vi",
    "sy":  "si",
    "hy":  "i",     # h malgache → souvent muet ou très léger
    # Voyelles spécifiques
    "ao":  "aou",   # diphtongue caractéristique
    "ai":  "aï",
    "oa":  "oua",
    "ia":  "ia",
    "io":  "iou",
    "eo":  "éou",
}

# Mots malgaches courants → transcription phonétique française
LEXIQUE = {
    "akory":      "a-kou-ri",
    "aby":        "a-bi",
    "manao":      "ma-naou",
    "ahoana":     "a-hou-na",        # 'h' quasi-muet, finale '-na' muette
    "misaotra":   "mi-saou-tra",
    "mazoto":     "ma-zou-tou",
    "veloma":     "vé-lou-ma",
    "androany":   "an-droua-ni",
    "lisany":     "li-sa-ni",
    "tonga soa":  "toun-ga soua",
    "salama":     "sa-la-ma",
    "tsara":      "tsa-ra",
    "fitiavana":  "fi-tia-va-na",
    "fihavanana": "fi-ha-va-na-na",
    "tanana":     "ta-na-na",
    "tanàna":     "ta-na-na",
    "vary":       "va-ri",
    "omby":       "oum-bi",
    "alina":      "a-li-na",
    "hariva":     "a-ri-va",         # 'h' initial muet
    "maraina":    "ma-raï-na",
    "zaza":       "za-za",
    "ray":        "raï",
    "reny":       "ré-ni",
    "havana":     "a-va-na",
    "fady":       "fa-di",
    "lamba":      "lam-ba",
    "mofo":       "mou-fou",
    "ronono":     "rou-nou-nou",
    "rano":       "ra-nou",
    "antananarivo":"an-ta-na-na-ri-vou",
    "madagascar": "ma-da-gas-kar",
    "malagasy":   "ma-la-ga-si",
    "merina":     "mé-ri-na",
    "betsileo":   "bét-si-léou",
}

def accentuer_syllabe(mot: str) -> str:
    """
    En malgache, l'accent porte sur l'avant-dernière syllabe
    (pénultième) sauf si la dernière est '-na', '-ka', '-tra' etc.
    On découpe naïvement en syllabes CV et insère une virgule
    orthographique pour forcer l'accent gTTS.
    """
    # Voyelles malgaches
    voyelles = "aeiouàâäéèêëîïôùûü"

    syllabes = []
    courante = ""
    for ch in mot:
        courante += ch
        if ch.lower() in voyelles:
            syllabes.append(courante)
            courante = ""
    if courante:                          # consonne(s) finales
        if syllabes:
            syllabes[-1] += courante
        else:
            syllabes.append(courante)

    if len(syllabes) < 2:
        return mot

    # Règle : consonne finale muette → l'accent recule d'une syllabe
    # On allonge la voyelle de l'avant-dernière syllabe via redoublement
    idx = -2
    if len(syllabes) >= 2:
        avant_dern = syllabes[idx]
        # Allonger la voyelle accentuée
        elongee = ""
        for ch in avant_dern:
            elongee += ch
            if ch.lower() in voyelles:
                elongee += ch          # doublement → gTTS allonge légèrement
        syllabes[idx] = elongee

    return "".join(syllabes)


def appliquer_regles_finales(mot: str) -> str:
    """
    Règles phonétiques de fin de mot :
    - '-na' final → très bref (quasi muet, on l'atténue)
    - '-ka' final → presque muet
    - '-tra' final → 'tra' bref
    - 'a' final souvent abrégé
    - 'i' final → son 'i' allongé
    """
    m = mot.lower()
    # Finales quasi-muettes : on garde mais on n'allonge pas
    for finale in ("ana", "ina", "ona", "ena", "una"):
        if m.endswith(finale) and len(mot) > len(finale) + 1:
            return mot                  # laisser tel quel, pas d'allongement

    # '-i' final → accentuer
    if m.endswith("i") and len(mot) > 2:
        return mot[:-1] + "ii"         # gTTS lira le 'i' un peu plus long

    return mot


def translitterer_clusters(texte: str) -> str:
    """Remplace les groupes consonantiques malgaches par leur équivalent français."""
    for cluster, remplacement in sorted(CONSONNES_MG.items(), key=lambda x: -len(x[0])):
        texte = texte.replace(cluster, remplacement)
    return texte


def preparer_texte_malgache(texte: str) -> str:
    """
    Pipeline complet de pré-traitement phonétique malgache :
    1. Normalisation Unicode (voyelles accentuées)
    2. Substitution des mots connus (lexique)
    3. Translittération des clusters consonantiques
    4. Accentuation syllabique mot par mot
    5. Règles de finales
    6. Ponctuation rythmique (pauses naturelles)
    """
    # 1. Normalisation des voyelles accentuées
    rempl_unicode = {
        "ô": "o", "Ô": "O", "â": "a", "ê": "e", "î": "i", "û": "u",
        "à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u",
        "ñ": "n", "ç": "s",
        # Garder les accents utiles pour gTTS
        "é": "é", "è": "è",
    }
    for ancien, nouveau in rempl_unicode.items():
        texte = texte.replace(ancien, nouveau)

    # 2. Substitution lexique (avant toute autre transformation)
    texte_bas = texte.lower()
    for mot_mg, phonetique in sorted(LEXIQUE.items(), key=lambda x: -len(x[0])):
        if mot_mg in texte_bas:
            # Remplacement insensible à la casse
            pattern = re.compile(re.escape(mot_mg), re.IGNORECASE)
            texte = pattern.sub(phonetique, texte)

    # 3. Translittération clusters consonantiques
    texte = translitterer_clusters(texte)

    # 4. Accentuation syllabique mot par mot
    mots = texte.split()
    mots_traites = []
    for mot in mots:
        # Isoler la ponctuation
        ponctuation = ""
        noyau = mot
        while noyau and noyau[-1] in ".,!?;:":
            ponctuation = noyau[-1] + ponctuation
            noyau = noyau[:-1]
        if noyau:
            noyau = accentuer_syllabe(noyau)
            noyau = appliquer_regles_finales(noyau)
        mots_traites.append(noyau + ponctuation)
    texte = " ".join(mots_traites)

    # 5. Intonation chantante : pauses légères après groupes accentués
    #    On insère des virgules après les mots de 3+ syllabes (groupes toniques)
    mots = texte.split()
    resultat = []
    for i, mot in enumerate(mots):
        resultat.append(mot)
        voyelles_mot = sum(1 for c in mot if c.lower() in "aeiouéè")
        # Pause après mot polysyllabique (rythme malgache)
        if voyelles_mot >= 3 and not mot.endswith((",", ".", "!", "?", ";")):
            resultat.append(",")
    texte = " ".join(resultat)

    # 6. Nettoyage : supprimer les virgules doubles, espaces multiples
    texte = re.sub(r",\s*,", ",", texte)
    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


# ─────────────────────────────────────────────────────────────────────
# PARTIE 2 : POST-TRAITEMENT AUDIO (pydub)
# ─────────────────────────────────────────────────────────────────────

def post_traiter_audio(fichier_in: str, fichier_out: str) -> bool:
    """
    Modifie l'audio gTTS pour approcher une voix malgache :
    - Légère baisse de pitch (voix plus grave, chaleureuse)
    - Tempo légèrement ralenti (débit malgache plus posé)
    - Filtre passe-bas doux (moins crisp, plus naturel)
    - Normalisation du volume
    - Légère réverbération simulée (delay + mix)
    Retourne True si succès.
    """
    if not PYDUB_OK:
        return False

    try:
        audio = AudioSegment.from_mp3(fichier_in)

        # — Tempo légèrement ralenti (×0.92) via resampling —
        # Abaisser le sample rate → ralentit ET baisse le pitch
        # Puis remonter le sample rate → corrige le pitch partiellement
        # Effet net : voix plus grave et légèrement plus lente
        original_frame_rate = audio.frame_rate

        # Pitch down ~1.5 demi-tons : frame_rate × 2^(-1.5/12) ≈ × 0.916
        pitch_factor = 0.916
        audio_pitched = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": int(original_frame_rate * pitch_factor)}
        ).set_frame_rate(original_frame_rate)

        # — Filtre passe-bas à 5000 Hz (atténue les hautes fréquences stridentes) —
        audio_filtered = low_pass_filter(audio_pitched, 5000)

        # — Normalisation volume —
        audio_norm = normalize(audio_filtered)

        # — Réverbération simulée (simple delay + atténuation) —
        delay_ms = 38           # délai de réverbération court (pièce petite)
        decay_db = -14          # atténuation de l'écho
        silence = AudioSegment.silent(duration=delay_ms)
        echo = audio_norm - abs(decay_db)
        # Superposer l'écho décalé sur l'original
        audio_reverb = audio_norm.overlay(silence + echo)

        # — Légère amplification finale (+1 dB) —
        audio_final = audio_reverb + 1

        # Export MP3 haute qualité
        audio_final.export(fichier_out, format="mp3", bitrate="192k")
        return True

    except Exception as e:
        print(f"⚠️  Post-traitement audio échoué : {e}")
        return False


# ─────────────────────────────────────────────────────────────────────
# PARTIE 3 : LECTURE AUDIO
# ─────────────────────────────────────────────────────────────────────

def lire_audio(fichier: str):
    """Lecture du fichier MP3 via pygame (stable Windows/Linux/Mac)."""
    if PYGAME_OK:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(fichier)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
            return
        except Exception as e:
            print(f"⚠️  pygame : {e}")

    # Fallback : playsound
    try:
        from playsound import playsound
        playsound(fichier)
    except Exception as e:
        print(f"⚠️  playsound : {e}")
        print(f"   Ouvrez manuellement : {os.path.abspath(fichier)}")


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 75)
    print("🎤 SYNTHÈSE VOCALE MALGACHE - Version 2.0")
    print("   Phonétique malgache réelle + post-traitement audio pydub")
    print("=" * 75)

    if not PYDUB_OK:
        print("\n💡 Pour activer le post-traitement audio :")
        print("   pip install pydub pygame")
        print("   + installer ffmpeg : https://ffmpeg.org/download.html\n")

    texte = input("\n✍️  Texte à lire (malgache ou mélangé) :\n> ").strip()
    if not texte:
        print("❌ Aucun texte saisi.")
        return

    print("\n⏳ Analyse phonétique en cours...")
    texte_prepare = preparer_texte_malgache(texte)

    print(f"\n📝 Texte original  : {texte}")
    print(f"🔤 Texte préparé   : {texte_prepare}")

    fichier_brut   = "voix_mg_brute.mp3"
    fichier_final  = "voix_malgache_hd.mp3"

    try:
        print("\n⏳ Synthèse vocale gTTS...")
        tts = gTTS(text=texte_prepare, lang="fr", slow=False)
        tts.save(fichier_brut)
        print(f"✅ Audio brut généré : {fichier_brut}")

        fichier_a_lire = fichier_brut

        if PYDUB_OK:
            print("⏳ Post-traitement audio (pitch, réverbération, EQ)...")
            succes = post_traiter_audio(fichier_brut, fichier_final)
            if succes:
                print(f"✅ Audio final      : {fichier_final}")
                fichier_a_lire = fichier_final
            else:
                print("⚠️  Post-traitement échoué, lecture de l'audio brut.")

        print(f"\n🔊 Lecture : {fichier_a_lire}")
        time.sleep(0.3)
        lire_audio(fichier_a_lire)
        print("\n✅ Lecture terminée !")

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        print("Vérifiez votre connexion internet (gTTS en a besoin).")

    finally:
        # Nettoyage fichier temporaire brut
        if PYDUB_OK and os.path.exists(fichier_brut):
            try:
                os.remove(fichier_brut)
            except Exception:
                pass


if __name__ == "__main__":
    main()