from deep_translator import GoogleTranslator
from textblob import TextBlob


def split_text(text, max_len=300):
    """
    Découpe le texte en morceaux pour éviter les erreurs de traduction
    """
    words = text.split()
    chunks = []
    current = ""

    for word in words:
        if len(current) + len(word) < max_len:
            current += " " + word
        else:
            chunks.append(current.strip())
            current = word

    if current:
        chunks.append(current.strip())

    return chunks


def translate_text(text):
    """
    Traduit un texte long en plusieurs morceaux
    """
    chunks = split_text(text)
    translated_chunks = []

    for chunk in chunks:
        translated = GoogleTranslator(source='auto', target='en').translate(chunk)
        translated_chunks.append(translated)

    return " ".join(translated_chunks)


def analyze_full_text(text):
    """
    Analyse complète :
    - traduction
    - analyse phrase par phrase
    - score global
    """
    # Traduction sécurisée
    translated_text = translate_text(text)

    print("Texte traduit :\n", translated_text)
    print("-" * 50)

    blob = TextBlob(translated_text)

    total_polarity = 0
    details = []

    # Analyse phrase par phrase
    for sentence in blob.sentences:
        polarity = sentence.sentiment.polarity
        total_polarity += polarity

        if polarity > 0:
            sentiment = "positif"
        elif polarity < 0:
            sentiment = "négatif"
        else:
            sentiment = "neutre"

        details.append({
            "phrase": str(sentence),
            "sentiment": sentiment,
            "score": polarity
        })

    # Score global
    if len(blob.sentences) > 0:
        avg = total_polarity / len(blob.sentences)
    else:
        avg = 0

    if avg > 0:
        global_sentiment = "positif"
    elif avg < 0:
        global_sentiment = "négatif"
    else:
        global_sentiment = "neutre"

    return {
        "global_sentiment": global_sentiment,
        "score_global": avg,
        "details": details
    }


# 🔥 TEST
if __name__ == "__main__":
    text = """
    Tena ratsy ity vokatra ity.
    Tsy tiako mihitsy fa manahirana be.
    Fa indraindray mety tsara ihany.
    Mety ilaina amin'ny toe-javatra sasany.
    """

    result = analyze_full_text(text)

    print("\n=== RESULTAT GLOBAL ===")
    print("Sentiment global :", result["global_sentiment"])
    print("Score global :", result["score_global"])

    print("\n=== DETAILS ===")
    for d in result["details"]:
        print(d)