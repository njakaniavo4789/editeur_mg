from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_correcteur,
    routes_lemma,
    routes_autocomplete,
    routes_sentiment,
    routes_traduction,
    routes_tts,
    routes_ner,
    routes_chatbot,
)

app = FastAPI(title="Malagasy AI Editor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_correcteur.router, prefix="/api")
app.include_router(routes_lemma.router, prefix="/api")
app.include_router(routes_autocomplete.router, prefix="/api")
app.include_router(routes_sentiment.router, prefix="/api")
app.include_router(routes_traduction.router, prefix="/api")
app.include_router(routes_tts.router, prefix="/api")
app.include_router(routes_ner.router, prefix="/api")
app.include_router(routes_chatbot.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Malagasy AI Editor API - miasa!"}
