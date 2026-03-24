# Mpanoratra Malagasy AI — Éditeur de Texte Augmenté par l'IA

TP Machine Learning — ISPM M2 S1

## Membres du groupe
| Nom | Rôle |
|-----|------|
| ...  | Backend NLP |
| ...  | Frontend React |
| ...  | Data / Scraping |

## Fonctionnalités IA
- Correcteur orthographique (Levenshtein + dictionnaire)
- Vérification phonotactique (REGEX)
- Lemmatisation (prefix/suffix rules)
- Autocomplétion N-gram
- Traducteur mot-à-mot (LibreTranslate)
- Analyse de sentiment (Bag of Words)
- Synthèse vocale (edge-tts)
- Reconnaissance d'entités (NER)
- Chatbot assistant

## Lancement rapide
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Bibliographie
- tenymalagasy.org
- mg.wikipedia.org
- HuggingFace: malagasy-nlp/roberta-base-mg
- Helsinki-NLP/opus-mt-mg-en
