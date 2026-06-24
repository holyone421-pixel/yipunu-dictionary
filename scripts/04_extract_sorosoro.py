import requests
from bs4 import BeautifulSoup
import re
import json
import os

URL = "https://www.sorosoro.org/le-punu/"
OUTPUT_DIR = "data_clean"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sorosoro.json")

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

def extraire_paires(texte):
    paires = {}
    motif = re.compile(
        r'(?:^|\n)\s*([^\d\s]{1,30})\s*[-:]\s*((?:(?:[^\d\n]{1,30})\s?){1,4})',
        re.MULTILINE
    )
    for match in motif.finditer(texte):
        yipunu_raw = match.group(1).strip()
        francais_raw = match.group(2).strip().rstrip('.')
        if anti_chiffres(yipunu_raw) or anti_chiffres(francais_raw):
            continue
        if anti_noms_propres(yipunu_raw, francais_raw):
            continue
        if anti_phrases(yipunu_raw, francais_raw):
            continue
        mot_clean = normaliser(yipunu_raw)
        trad_clean = normaliser(francais_raw)
        if mot_clean and trad_clean:
            if mot_clean not in paires:
                paires[mot_clean] = []
            if trad_clean not in paires[mot_clean]:
                paires[mot_clean].append(trad_clean)
    return paires

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        response = requests.get(URL, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        texte = soup.get_text(separator='\n')
        paires = extraire_paires(texte)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(paires, f, ensure_ascii=False, indent=2)
        print(f"{len(paires)} entrées extraites de Sorosoro et sauvegardées dans {OUTPUT_FILE}")
    except Exception as e:
        print(f"Erreur lors de l'extraction Sorosoro : {e}")

if __name__ == "__main__":
    main()
