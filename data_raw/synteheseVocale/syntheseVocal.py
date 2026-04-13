"""
╔══════════════════════════════════════════════════════════╗
║   TTS MALGACHE v2 – Vraie voix malgache                 ║
║   Modèle : facebook/mms-tts-mlg (Meta AI)               ║
║   100% gratuit, offline, aucun API payant                ║
╚══════════════════════════════════════════════════════════╝

PRINCIPE :
  Ce programme utilise le modèle VITS entraîné par Meta AI
  spécifiquement sur la langue malgache (ISO 639-3 : mlg).
  Le modèle génère une vraie voix malgache native, sans
  approximation phonétique.

INSTALLATION (une seule fois) :
  pip install transformers torch scipy pydub numpy

  Optionnel (lecture audio) :
  pip install pygame
  ou
  pip install playsound==1.2.2

  Sur Linux :
  sudo apt install ffmpeg libsndfile1

  Sur macOS :
  brew install ffmpeg libsndfile
"""

import os
import sys
import argparse
import tempfile
import numpy as np

# ── Vérification des dépendances ────────────────────────

def check_deps():
    missing = []
    for pkg in ['transformers', 'torch', 'scipy']:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[ERREUR] Bibliothèques manquantes : {', '.join(missing)}")
        print("         Lancez : pip install " + " ".join(missing))
        sys.exit(1)

check_deps()

import torch
import scipy.io.wavfile
from transformers import VitsModel, AutoTokenizer

# ── Lecture audio ────────────────────────────────────────

try:
    from pydub import AudioSegment
    from pydub.effects import speedup
    PYDUB_OK = True
except ImportError:
    PYDUB_OK = False
    print("[ATTENTION] pydub absent – effets audio désactivés.")

try:
    import pygame
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False

try:
    from playsound import playsound
    PLAYSOUND_OK = True
except ImportError:
    PLAYSOUND_OK = False


# ════════════════════════════════════════════════════════
#  1. CHARGEMENT DU MODÈLE MALGACHE
#     facebook/mms-tts-mlg — modèle VITS de Meta AI
#     Téléchargé automatiquement (~100 MB) au premier lancement
# ════════════════════════════════════════════════════════

MODEL_ID = "facebook/mms-tts-mlg"
_model = None
_tokenizer = None


def load_model():
    """
    Charge le modèle TTS malgache de Facebook (une seule fois en mémoire).
    Le modèle est mis en cache automatiquement par Hugging Face.
    """
    global _model, _tokenizer
    if _model is None:
        print("[INFO] Chargement du modèle facebook/mms-tts-mlg...")
        print("       (Premier lancement : ~100 MB téléchargés depuis Hugging Face)")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _model = VitsModel.from_pretrained(MODEL_ID)
        _model.eval()  # mode inférence (pas d'entraînement)
        print("[INFO] Modèle chargé avec succès ✓")
    return _model, _tokenizer


# ════════════════════════════════════════════════════════
#  2. PRÉTRAITEMENT DU TEXTE MALGACHE
#     Normalisation légère avant envoi au modèle
# ════════════════════════════════════════════════════════

def preprocess_malagasy(text: str) -> str:
    """
    Normalise le texte malgache pour le modèle VITS :
      - Supprime les caractères non supportés
      - Normalise les espaces
      - Met en minuscules (le modèle est sensible à la casse)
    """
    # Le modèle a été entraîné sur du texte malgache en minuscules
    text = text.strip().lower()

    # Remplace les tirets longs et caractères spéciaux
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace("'", "'").replace("'", "'")

    # Supprime les caractères non ASCII sauf les lettres accentuées usuelles
    allowed_extras = set("àâäéèêëîïôùûü-.,!?;:' ")
    cleaned = ''.join(c for c in text if c.isalpha() or c.isdigit() or c in allowed_extras)

    # Normalise les espaces multiples
    cleaned = ' '.join(cleaned.split())

    return cleaned


# ════════════════════════════════════════════════════════
#  3. GÉNÉRATION AUDIO AVEC LE MODÈLE MALGACHE
# ════════════════════════════════════════════════════════

def generate_audio_mlg(text: str, speaking_rate: float = 1.0) -> tuple:
    """
    Génère un tableau numpy de forme d'onde audio à partir du texte malgache.

    Paramètres :
        text          : texte malgache normalisé
        speaking_rate : vitesse de parole (0.8 = lent, 1.0 = normal, 1.2 = rapide)

    Retourne : (waveform: np.ndarray, sample_rate: int)
    """
    model, tokenizer = load_model()

    # Tokenisation du texte
    inputs = tokenizer(text, return_tensors="pt")

    # Ajustement du débit via le paramètre interne du modèle VITS
    # speaking_rate modifie la durée prédite de chaque phonème
    if hasattr(model, 'speaking_rate'):
        model.speaking_rate = speaking_rate

    # Génération de la forme d'onde (sans calcul de gradient = plus rapide)
    with torch.no_grad():
        # On fixe le seed pour une génération reproductible
        torch.manual_seed(42)
        output = model(**inputs)

    # Extraction de la forme d'onde (shape : [1, 1, T] ou [1, T])
    waveform = output.waveform.squeeze().numpy()

    sample_rate = model.config.sampling_rate  # généralement 16000 Hz

    return waveform, sample_rate


# ════════════════════════════════════════════════════════
#  4. POST-TRAITEMENT AUDIO
#     Amélioration de la qualité et ajustements pitch/tempo
# ════════════════════════════════════════════════════════

def normalize_audio(waveform: np.ndarray) -> np.ndarray:
    """Normalise l'amplitude pour éviter la saturation."""
    max_val = np.abs(waveform).max()
    if max_val > 0:
        waveform = waveform / max_val * 0.95
    return waveform


def save_wav(waveform: np.ndarray, sample_rate: int) -> str:
    """
    Sauvegarde la forme d'onde dans un fichier WAV temporaire.
    Retourne le chemin du fichier.
    """
    waveform = normalize_audio(waveform)
    # Conversion en int16 pour scipy
    waveform_int = (waveform * 32767).astype(np.int16)

    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    scipy.io.wavfile.write(tmp.name, sample_rate, waveform_int)
    return tmp.name


def apply_audio_effects(wav_path: str, pitch_semitones: int = 0, speed: float = 1.0) -> str:
    """
    Applique des effets audio via pydub :
      - pitch_semitones : décalage de hauteur (+2 = plus aigu, -2 = plus grave)
      - speed           : facteur de vitesse (0.9 = 10% plus lent)

    Retourne le chemin du fichier WAV modifié.
    """
    if not PYDUB_OK:
        return wav_path

    audio = AudioSegment.from_wav(wav_path)
    original_rate = audio.frame_rate

    # ── Ajustement du pitch ──
    if pitch_semitones != 0:
        new_rate = int(original_rate * (2 ** (pitch_semitones / 12.0)))
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
        audio = audio.set_frame_rate(original_rate)

    # ── Ajustement du tempo ──
    if speed > 1.0:
        audio = speedup(audio, playback_speed=speed, chunk_size=150)
    elif speed < 1.0 and speed > 0:
        slow_rate = int(original_rate * speed)
        audio = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": slow_rate}
        ).set_frame_rate(original_rate)

    # ── Normalisation du volume ──
    audio = audio.normalize()

    out = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    audio.export(out.name, format='wav')
    os.unlink(wav_path)
    return out.name


# ════════════════════════════════════════════════════════
#  5. LECTURE AUDIO
# ════════════════════════════════════════════════════════

def play_audio(filepath: str):
    """Lit le fichier audio WAV selon les bibliothèques disponibles."""

    if PYGAME_OK:
        pygame.mixer.init(frequency=16000)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

    elif PLAYSOUND_OK:
        playsound(filepath)

    else:
        print(f"[INFO] Fichier audio : {filepath}")
        if sys.platform == 'darwin':
            os.system(f'afplay "{filepath}"')
        elif sys.platform.startswith('linux'):
            os.system(f'aplay "{filepath}" 2>/dev/null || mpg123 "{filepath}" 2>/dev/null')
        elif sys.platform == 'win32':
            os.startfile(filepath)
        else:
            print("[INFO] Impossible de lire automatiquement. Ouvrez le fichier manuellement.")


# ════════════════════════════════════════════════════════
#  6. MODES VOIX
#     Préréglages pour voix homme / femme / neutre
# ════════════════════════════════════════════════════════

VOICE_PRESETS = {
    'neutre': {
        'pitch_semitones': 0,
        'speed': 1.0,
        'speaking_rate': 1.0,
        'description': 'Voix neutre du modèle (recommandé pour commencer)'
    },
    'femme': {
        'pitch_semitones': +3,    # +3 demi-tons = voix plus aiguë
        'speed': 1.0,
        'speaking_rate': 0.95,
        'description': 'Simulation voix féminine (pitch relevé)'
    },
    'homme': {
        'pitch_semitones': -3,    # -3 demi-tons = voix plus grave
        'speed': 0.95,
        'speaking_rate': 1.05,
        'description': 'Simulation voix masculine (pitch abaissé)'
    },
}


# ════════════════════════════════════════════════════════
#  7. PROGRAMME PRINCIPAL
# ════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="TTS Malgache v2 – Vraie voix malgache (facebook/mms-tts-mlg)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples de textes malgaches :
  "manao ahoana ianao"         → Comment allez-vous ?
  "misaotra betsaka"           → Merci beaucoup
  "faly mahita anao"           → Content de vous voir
  "veloma"                     → Au revoir
  "tiako ianao"                → Je t'aime
  "mora mora"                  → Doucement
  "tsara ny andro anio"        → Il fait beau aujourd'hui
        """
    )
    parser.add_argument(
        '--voix', '-v',
        choices=['neutre', 'femme', 'homme'],
        default='neutre',
        help="Type de voix : neutre / femme / homme (défaut: neutre)"
    )
    parser.add_argument(
        '--texte', '-t',
        type=str,
        default=None,
        help="Texte malgache à lire directement (sans saisie interactive)"
    )
    parser.add_argument(
        '--sauvegarder', '-s',
        type=str,
        default=None,
        metavar='FICHIER.wav',
        help="Sauvegarder l'audio dans un fichier WAV au lieu de le lire"
    )
    parser.add_argument(
        '--vitesse',
        type=float,
        default=None,
        help="Vitesse manuelle (ex: 0.85 = lent, 1.2 = rapide)"
    )
    args = parser.parse_args()

    # ── Bannière ──
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   🎙️  TTS MALGACHE v2 — facebook/mms-tts-mlg        ║")
    print("║   Vraie voix malgache, modèle Meta AI               ║")
    print("╚══════════════════════════════════════════════════════╝")

    preset = VOICE_PRESETS[args.voix]
    print(f"\n   Voix      : {args.voix} — {preset['description']}")

    speed_final = args.vitesse if args.vitesse else preset['speed']
    print(f"   Vitesse   : {speed_final}")
    print()

    # ── Saisie du texte ──
    if args.texte:
        texte = args.texte
    else:
        print("Entrez votre texte en malgache (puis appuyez sur Entrée) :")
        print("Exemple : manao ahoana ianao\n")
        texte = input(">>> ").strip()

    if not texte:
        print("[ERREUR] Aucun texte saisi.")
        sys.exit(1)

    # ── Étape 1 : Prétraitement ──
    print("\n[1/4] Prétraitement du texte...")
    texte_clean = preprocess_malagasy(texte)
    print(f"      Original  : {texte}")
    print(f"      Nettoyé   : {texte_clean}")

    # ── Étape 2 : Génération audio ──
    print("\n[2/4] Génération de la voix malgache (VITS)...")
    print("      (Peut prendre 5-15 secondes selon votre machine)")
    try:
        waveform, sample_rate = generate_audio_mlg(
            texte_clean,
            speaking_rate=preset['speaking_rate']
        )
    except Exception as e:
        print(f"\n[ERREUR] Génération échouée : {e}")
        print("         Vérifiez votre connexion internet (premier téléchargement du modèle)")
        sys.exit(1)

    print(f"      ✓ Audio généré ({len(waveform)/sample_rate:.2f} secondes, {sample_rate} Hz)")

    # ── Étape 3 : Sauvegarde WAV ──
    print("\n[3/4] Enregistrement WAV temporaire...")
    wav_path = save_wav(waveform, sample_rate)

    # ── Étape 4 : Post-traitement (pitch / tempo) ──
    print("[4/4] Ajustements audio (pitch / tempo)...")
    wav_path = apply_audio_effects(
        wav_path,
        pitch_semitones=preset['pitch_semitones'],
        speed=speed_final
    )

    # ── Sauvegarde ou lecture ──
    if args.sauvegarder:
        import shutil
        shutil.copy(wav_path, args.sauvegarder)
        os.unlink(wav_path)
        print(f"\n✅ Fichier audio sauvegardé : {args.sauvegarder}")
    else:
        print("\n🔊 Lecture en cours...\n")
        play_audio(wav_path)
        try:
            os.unlink(wav_path)
        except Exception:
            pass
        print("\n✅ Lecture terminée.")


# ════════════════════════════════════════════════════════
#  MODE INTERACTIF EN BOUCLE (bonus)
# ════════════════════════════════════════════════════════

def mode_interactif():
    """
    Mode interactif : saisit et lit plusieurs textes en boucle.
    Usage : python malagasy_tts_v2.py --interactif
    """
    print("\n🎙️  Mode interactif – Tapez 'quitter' pour arrêter\n")
    load_model()  # Pré-chargement du modèle

    voix_actuelle = 'neutre'

    while True:
        print(f"\n[Voix: {voix_actuelle}] Entrez un texte malgache (ou 'voix:homme/femme/neutre') :")
        entree = input(">>> ").strip()

        if entree.lower() in ('quitter', 'exit', 'q'):
            print("Au revoir! Veloma!")
            break

        if entree.lower().startswith('voix:'):
            nouvelle_voix = entree.split(':')[1].strip().lower()
            if nouvelle_voix in VOICE_PRESETS:
                voix_actuelle = nouvelle_voix
                print(f"✓ Voix changée : {voix_actuelle}")
            else:
                print(f"[ERREUR] Voix inconnue. Choix : {', '.join(VOICE_PRESETS.keys())}")
            continue

        if not entree:
            continue

        try:
            texte_clean = preprocess_malagasy(entree)
            preset = VOICE_PRESETS[voix_actuelle]
            waveform, sample_rate = generate_audio_mlg(texte_clean, preset['speaking_rate'])
            wav_path = save_wav(waveform, sample_rate)
            wav_path = apply_audio_effects(wav_path, preset['pitch_semitones'], preset['speed'])
            print("🔊 Lecture...")
            play_audio(wav_path)
            try:
                os.unlink(wav_path)
            except Exception:
                pass
        except Exception as e:
            print(f"[ERREUR] {e}")


# ════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Détection du mode interactif en boucle
    if '--interactif' in sys.argv or '-i' in sys.argv:
        mode_interactif()
    else:
        main()


# ════════════════════════════════════════════════════════
#  RÉSUMÉ DES COMMANDES
# ════════════════════════════════════════════════════════
"""
─────────────────────────────────────────────────────────
  INSTALLATION
─────────────────────────────────────────────────────────
  pip install transformers torch scipy pydub pygame

  Linux :   sudo apt install ffmpeg libsndfile1
  macOS :   brew install ffmpeg libsndfile

─────────────────────────────────────────────────────────
  UTILISATION
─────────────────────────────────────────────────────────

  # Saisie interactive (voix neutre)
  python malagasy_tts_v2.py

  # Voix féminine
  python malagasy_tts_v2.py --voix femme

  # Voix masculine, texte direct
  python malagasy_tts_v2.py --voix homme --texte "manao ahoana ianao"

  # Vitesse personnalisée (lent)
  python malagasy_tts_v2.py --vitesse 0.80

  # Sauvegarder l'audio dans un fichier
  python malagasy_tts_v2.py --texte "veloma" --sauvegarder sortie.wav

  # Mode interactif en boucle (changer de voix en cours de session)
  python malagasy_tts_v2.py --interactif

─────────────────────────────────────────────────────────
  À PROPOS DU MODÈLE
─────────────────────────────────────────────────────────
  facebook/mms-tts-mlg est un modèle VITS (Variational
  Inference with adversarial learning for end-to-end TTS)
  entraîné par Meta AI sur des données audio malgaches
  dans le cadre du projet MMS (Massively Multilingual Speech).

  Il produit une voix malgache native, sans approximation.
  Taille : ~100 MB (téléchargé automatiquement au 1er lancement)
  Licence : CC-BY-NC 4.0

─────────────────────────────────────────────────────────
"""