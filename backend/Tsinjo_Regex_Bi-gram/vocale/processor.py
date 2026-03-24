import re

class MalagasyProcessor:
    def clean(self, text: str) -> str:
        # Mise en minuscule
        text = text.lower().strip()

        # Remplacement des chiffres par des mots malgaches
        replacements = {
            "0": "aotra", "1": "iray", "2": "roa", "3": "telo",
            "4": "efatra", "5": "dimy", "6": "enina",
            "7": "fito", "8": "valo", "9": "sivy"
        }
        for num, word in replacements.items():
            text = text.replace(num, word)

        # On ne garde que les lettres et les espaces
        text = re.sub(r'[^a-zàâéèêëîïôûùç\s]', '', text)

        return text