# Scriptura — Éditeur de Texte Malagasy Augmenté par l'IA

TP Machine Learning — ISPM M2 S1

---

## Qu'est-ce que c'est ?

Un éditeur de texte intelligent pour la langue malagasy doté de fonctionnalités IA avancées :

| Fonctionnalité | Description |
|----------------|-------------|
| ✏️ **Correction orthographique** | Détection d'erreurs avec suggestions (Fuzzy matching Levenshtein) |
| 🔤 **Lemmatisation** | Analyse morphologique (préfixes/suffixes) |
| 💡 **Autocomplétion** | Prédiction du mot suivant (Markov Bigramme) |
| 😊 **Analyse de sentiments** | Détection POSITIF/NEGATIF/NEUTRE |
| 🗣️ **Synthèse vocale (TTS)** | Conversion texte → audio (facebook/mms-tts-mlg) |
| 🤖 **Chatbot assistant** | Assistant IA basé sur Gemini |
| 🌐 **Traduction** | Dictionnaire MG → FR |
| 🏷️ **NER** | Reconnaissance d'entités nommées (villes, personnes) |

---

## Tester maintenant

1. **Backend Colab doit tourner** avec `VITE_API_URL` configurée
2. Ouvrez : **https://whimsical-crisp-bb4e10.netlify.app/**
3. Tapez du texte en malagasy (au moins 2 mots pour NER)
4. La barre de droite affiche automatiquement :
   - **Entités (NER)** détectées (villes, personnes)
   - **Fanitsiana** (suggestions de correction)
   - **Lematisera** (préfixe/infixe/suffixe/racine)
   - **Fandikana** (traduction MG→FR)
   - **Autocomplete** (mots suivants possibles)

---

## Architecture

```
┌─────────────────┐         ┌─────────────────────┐
│   Netlify        │  HTTPS   │   Google Colab      │
│  (Frontend)      │────────▶│   (Backend API)     │
│  https://...    │   API   │   + ngrok tunnel    │
└─────────────────┘         └─────────────────────┘
```

- **Frontend** : Hébergé sur Netlify (React/Vite)
- **Backend** : API Python FastAPI sur Google Colab avec ngrok

---

## API Endpoints

| Route | Méthode | Description |
|------|---------|-------------|
| `/api/correct/mot` | POST | Correction orthographique |
| `/api/correct/texte` | POST | Correction d'un texte complet |
| `/api/lemma` | POST | Lemmatisation d'un mot |
| `/api/lemma/analyse` | POST | Analyse morphologique |
| `/api/complete` | POST | Autocomplétion |
| `/api/sentiment` | POST | Analyse de sentiments |
| `/api/translate` | POST | Traduction MG → FR |
| `/api/tts` | POST | Synthèse vocale |
| `/api/ner` | POST | Reconnaissance d'entités |
| `/api/chat` | POST | Chatbot Gemini |

---

## Technologies utilisées

### Frontend
- React 18 + Vite
- Quill Editor
- TailwindCSS
- Zustand (state management)
- Axios

### Backend
- FastAPI (Python)
- RapidFuzz (correction orthographique)
- Transformers (TTS MMS)
- Google Generative AI (Gemini chatbot)

---

## Membres du groupe

| Membre | GitHub | Rôle |
|--------|--------|------|
| RatsirofoFenosoa-Git | [GitHub](https://github.com/RatsirofoFenosoa-Git) | Backend NLP |
| Tiji-Tahina | [GitHub](https://github.com/Tiji-Tahina) | Backend NLP |
| njakaniavo4789 | [GitHub](https://github.com/njakaniavo4789) | Frontend React |
| Devkalix | [GitHub](https://github.com/Devkalix) | Frontend React |
| TatumLn | [GitHub](https://github.com/TatumLn) | DevOps / Data |
| Toby7431 | [GitHub](https://github.com/Toby7431) | DevOps / Backend NLP |

---

## Vidéo de présentation

[Voir la vidéo](https://drive.google.com/file/d/13_4-HVYdgCsw_HQSM8EOP7vNilxp5ZSh/view?usp=sharing)
[Presentation final](https://drive.google.com/file/d/1bGXncuAOPnXggw1RUWA1lQa7GVNjGzLz/view?usp=sharing)