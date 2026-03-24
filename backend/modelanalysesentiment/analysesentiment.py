from googletrans import Translator
from textblob import TextBlob

translator = Translator()

def analyze_malagasy(text):
    # Traduction vers anglais
    translated = translator.translate(text, dest='en').text
    
    # Analyse sentiment
    blob = TextBlob(translated)
    polarity = blob.sentiment.polarity

    if polarity > 0:
        return "positif"
    elif polarity < 0:
        return "négatif"
    else:
        return "neutre"


text = "Tena tsara ity vokatra ity"
print(analyze_malagasy(text))