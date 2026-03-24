# Mpanoratra Malagasy AI — Éditeur de Texte Augmenté par l'IA

TP Machine Learning — ISPM M2 S1

---

## Table des matières

1. [Fonctionnalités IA](#fonctionnalités-ia)
2. [Scraping — tenymalagasy.org avec triage](#scraping--tenymalagasyorg-avec-triage)
3. [Scraping — mg.wikipedia.org par thèmes](#scraping--mgwikipediaorg-par-thèmes)
4. [Vérification à base de règles (Regex)](#vérification-à-base-de-règles-regex)
5. [Correction orthographique — Levenshtein & Hash](#correction-orthographique--levenshtein--tables-de-hachage)
6. [Lemmatisation](#lemmatisation)
7. [Autocomplétion — Modèle de Markov Bigramme](#autocompletion--modèle-de-markov-bigramme)
8. [Modèle bigramme pré-entraîné & probabilités](#modèle-bigramme-pré-entraîné--probabilités)
9. [Analyse de sentiments](#analyse-de-sentiments)
10. [Interface utilisateur](#interface-utilisateur)
11. [Installation rapide](#installation-rapide)
12. [Bibliographie](#bibliographie)
13. [Membres du groupe](#membres-du-groupe)

---

## Fonctionnalités IA

| Module | Technologie |
|--------|-------------|
| Correcteur orthographique | Levenshtein + tables de hachage |
| Vérification phonotactique | Regex |
| Lemmatisation | Règles préfixes / suffixes |
| Autocomplétion | Modèle de Markov bigramme |
| Traducteur | LibreTranslate + Helsinki-NLP |
| Analyse de sentiment | Bag of Words + RoBERTa MG |
| Synthèse vocale | edge-tts (mg-MG-VahinyNeural) |
| Reconnaissance d'entités | NER (villes + noms propres MG) |
| Chatbot assistant | LangChain + Flowise |

---

## Scraping — tenymalagasy.org avec triage

### Contexte & rôle dans le projet

Pour alimenter les modules de **lemmatisation**, de **correction orthographique** et d'**autocomplétion**, nous avons eu besoin d'un dictionnaire structuré de la langue malagasy. Plutôt que de le construire manuellement, nous avons utilisé **n8n** — un outil d'automatisation open-source — pour scraper automatiquement le site [tenymalagasy.org](https://tenymalagasy.org).

Le workflow n8n parcourt les 20 lettres disponibles (A, B, D … Z), extrait pour chacune tous les **fototeny** (mots racines), leurs **sampateny** (mots dérivés) ainsi que la **lettre** d'appartenance, puis exporte le tout dans un fichier **CSV trié alphabétiquement**.

Ce fichier CSV est sauvegardé dans le dossier **`data_raw/`** du projet :

```
data_raw/
└── fototeny_sampateny_lettre.csv    ← généré par n8n, colonnes : lettre | fototeny | sampateny
```

Il est ensuite utilisé directement par plusieurs modules :

| Module | Utilisation du CSV |
|--------|--------------------|
| **Lemmatisation** | Liste des fototeny comme référence de racines valides |
| **Correcteur orthographique** | Construction de la table de hachage + index de suggestions |
| **Vérification Regex** | Validation des terminaisons et préfixes connus |
| **Autocomplétion N-gram** | Enrichissement du vocabulaire du corpus d'entraînement |

### Objectif
Récupérer tous les **fototeny** (mots racines) et leurs **sampateny** (mots dérivés)
pour les 20 lettres disponibles, avec un **triage automatique** par lettre dans un
fichier CSV unique.

### Workflow n8n

```
[Manual Trigger]
      ↓
[Code — Générer lettres]      → 20 items { lettre, param }
      ↓
[HTTP Request]                → GET /bins/rootLists?o=let{x}
      ↓
[Code — Extraction + Triage]  → parse table.menuLink, split <tr>
      ↓
[Google Sheets — Append]      → une ligne par fototeny
```

### Schéma CSV final (trié)

```
lettre | fototeny  | sampateny
-------|-----------|--------------------------------------
A      | ady       | fifadian-kanina, miady, voady
A      | afo       | afobe, mampiafo, voafo
B      | ba        | fiba, mibà, mpiba
B      | baba      | mibaba
...
Z      | zara      | mizara, zaraina, fizarana
```

---

## Scraping — mg.wikipedia.org par thèmes

### Thèmes ciblés

| Thème Wikipedia MG | URL |
|--------------------|-----|
| Madagasikara | `https://mg.wikipedia.org/wiki/Madagasikara` |
| Tantara | `https://mg.wikipedia.org/wiki/Tantara` |
| Politika | `https://mg.wikipedia.org/wiki/Politika` |
| Tontolo iainana | `https://mg.wikipedia.org/wiki/Tontolo_iainana` |

## Correction orthographique — Levenshtein & Tables de hachage

### Approche hybride

```
Mot saisi
   ↓
[Table de hachage]   →  correspondance exacte ?  →  OUI → retourner le mot
   ↓ NON
[Index par préfixe]  →  filtrer candidats (même 2 premières lettres)
   ↓
[Distance Levenshtein]  →  top-5 suggestions triées par score
```

### Flux de données temps réel

```
Utilisateur tape un mot
        ↓  POST /api/correct   (debounce 300ms)
        →  Suggestions Levenshtein dans la sidebar

Utilisateur appuie sur Espace
        ↓  POST /api/complete  { "mot": "dernier_mot" }
        →  Dropdown : ny (8.4%) · fanahy (6.3%) · fiainana (5.9%)

Bouton "Analyser" cliqué
        ↓  POST /api/sentiment { "texte": "..." }
        →  Jauge POSITIF 94.2%
```

### Aperçu

```
┌─────────────────────────────────────────────────────────────────┐
│  [Correcteur ✓]  [TTS ▶]  [Traduire ⇄]  [Analyser ☺]          │
├──────────────────────────────────────┬──────────────────────────┤
│                                      │  CORRECTEUR              │
│  Ny fiainan'ny Malagasy dia tsara    │  mibaly → mibaby  (91%) │
│  be. Mibaby ny ankizy ary mifalia|   │  mibika → mibika  (83%) │
│                                      │                          │
│  [ ny     (23.4%) ]                  │  SENTIMENT               │
│  [ izy    (18.2%) ]                  │  ██████████░░ POSITIF    │
│  [ ireo    (9.1%) ]                  │         94.2%            │
└──────────────────────────────────────┴──────────────────────────┘
```

---

## Installation rapide

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev

# Docker (tout-en-un)
docker-compose up --build
# Backend  → http://localhost:8000
# Frontend → http://localhost:3000
# API docs → http://localhost:8000/docs
```

---

## Bibliographie

- [tenymalagasy.org](https://tenymalagasy.org) — Dictionnaire & fototeny
- [mg.wikipedia.org](https://mg.wikipedia.org) — Corpus thématique malagasy
- [HuggingFace — malagasy-nlp/roberta-base-mg](https://huggingface.co/malagasy-nlp/roberta-base-mg)
- [Helsinki-NLP/opus-mt-mg-en](https://huggingface.co/Helsinki-NLP/opus-mt-mg-en)
- [LibreTranslate](https://libretranslate.com)
- [edge-tts](https://github.com/rany2/edge-tts)
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz)

---

## Membres du groupe

| Membre | Rôle |
|--------|------|
| [RatsirofoFenosoa-Git](https://github.com/RatsirofoFenosoa-Git) | Backend NLP |
| [Tiji-Tahina](https://github.com/Tiji-Tahina) | Backend NLP |
| [njakaniavo4789](https://github.com/njakaniavo4789) | Frontend React |
| [Devkalix](https://github.com/Devkalix) | Frontend React |
| [TatumLn](https://github.com/TatumLn) | DevOps / Data / Scraping |
| [Toby7431](https://github.com/Toby7431) | Devops / Backend NLP |
