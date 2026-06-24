import requests
from bs4 import BeautifulSoup
import re, json, os

# Liste des blogs à scraper (vous pouvez en ajouter)
BLOGS = [
    "https://mawandza-minyondu.blogspot.com/",
    # Ajoutez d'autres URLs de blogs ici
]

OUTPUT_DIR = "data_clean"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "blogs.json")

def anti_chiffres(s):
    return bool(re.search(r'\d', s))

def anti_noms_propres(y, f):
    return (y and y[0].isupper()) or (f and f[0].isupper())

def anti_phrases(y, f):
    return len(y.split()) > 3 or len(f.split()) > 4

def normaliser(mot):
    mot = re.sub(r'\(.*?\)', '', mot)
    mot = re.sub(r'^-|-$', '', mot)
    return mot.strip()

def extraire_paires(texte):
    motif = re.compile(
        r'([^\d\s]{1,30})\s*[:,\-]\s*((?:(?:[^\d\n]{1,30})\s?){1,4})',
        re.MULTILINE
    )
    paires = {}
    for m in motif.finditer(texte):
        y = m.group(1).strip()
        f = m.group(2).strip().rstrip('.')
        if anti_chiffres(y) or anti_chiffres(f): continue
        if anti_noms_propres(y, f): continue
        if anti_phrases(y, f): continue
        yc, fc = normaliser(y), normaliser(f)
        if yc and fc:
            paires.setdefault(yc, [])
            if fc not in paires[yc]: paires[yc].append(fc)
    return paires

def scraper_blog(url):
    try:
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.content, 'html.parser')
        for s in soup(["script", "style"]): s.decompose()
        texte = soup.get_text(separator='\n')
        paires = extraire_paires(texte)
        print(f"{url} : {len(paires)} entrées")
        return paires
    except Exception as e:
        print(f"Erreur {url}: {e}")
        return {}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dico = {}
    for blog in BLOGS:
        p = scraper_blog(blog)
        for mot, trads in p.items():
            dico.setdefault(mot, [])
            for t in trads:
                if t not in dico[mot]: dico[mot].append(t)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dico, f, ensure_ascii=False, indent=2)
    print(f"Total blogs : {len(dico)} mots")

if __name__ == "__main__":
    main()
