import requests
from bs4 import BeautifulSoup
import json
import re
import os

URL = "https://mylittlewordland.com"   # À adapter une fois qu'on connaîtra la vraie page du tableau
OUTPUT_DIR = "data_clean"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "wordland.json")

def anti_chiffres(chaine):
    return bool(re.search(r'\d', chaine))

def anti_noms_propres(mot_yipunu, trad_fr):
    if mot_yipunu and mot_yipunu[0].isupper():
        return True
    if trad_fr and trad_fr[0].isupper():
        return True
    return False

def anti_phrases(cle_yipunu, bloc_fr):
    return len(cle_yipunu.split()) > 3 or len(bloc_fr.split()) > 4

def normaliser(mot):
    mot = re.sub(r'\(.*?\)', '', mot)
    mot = re.sub(r'^-|-$', '', mot)
    mot = mot.strip()
    return mot

def extract_table():
    response = requests.get(URL, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    if not table:
        print("Aucun tableau trouvé.")
        return {}
    rows = table.find_all('tr')
    dictionnaire = {}
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 2:
            yipunu_raw = cols[0].get_text(strip=True)
            francais_raw = cols[1].get_text(strip=True)
            if yipunu_raw.lower() in ['yipunu', 'mot yipunu', '']:
                continue
            if anti_chiffres(yipunu_raw) or anti_chiffres(francais_raw):
                continue
            if anti_noms_propres(yipunu_raw, francais_raw):
                continue
            if anti_phrases(yipunu_raw, francais_raw):
                continue
            mot_clean = normaliser(yipunu_raw)
            trad_clean = normaliser(francais_raw)
            if mot_clean and trad_clean:
                if mot_clean not in dictionnaire:
                    dictionnaire[mot_clean] = []
                if trad_clean not in dictionnaire[mot_clean]:
                    dictionnaire[mot_clean].append(trad_clean)
    return dictionnaire

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = extract_table()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(data)} entrées sauvegardées dans {OUTPUT_FILE}")
