"""
Script: scrape_tenymalagasy.py
Tanjona: Mandray teny sy famaritana avy amin'ny tenymalagasy.org
Ampiasao: python -m app.scripts.scrape_tenymalagasy
"""
import requests
from bs4 import BeautifulSoup
import json, time, os

OUTPUT = os.path.join(os.path.dirname(__file__), "../data/dictionnaire_mg.json")
LETTRES = "abcdefghiklmnoprstvy"

def scrape():
    dictionnaire = {}
    for lettre in LETTRES:
        url = f"https://tenymalagasy.org/bins/teny2.cgi?litera={lettre}"
        print(f"Scraping: {lettre}...")
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            # Adapter les selectors selon la structure réelle du site
            for item in soup.select(".entrytitle"):
                mot = item.get_text(strip=True)
                definition = ""
                next_el = item.find_next_sibling()
                if next_el:
                    definition = next_el.get_text(strip=True)
                if mot:
                    dictionnaire[mot.lower()] = definition
        except Exception as e:
            print(f"Erreur {lettre}: {e}")
        time.sleep(1.5)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(dictionnaire, f, ensure_ascii=False, indent=2)
    print(f"Vita! {len(dictionnaire)} teny voatahiry.")

if __name__ == "__main__":
    scrape()
