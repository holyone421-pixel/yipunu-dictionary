import os
import re
import json
from pypdf import PdfReader

INPUT_DIR = "data_raw"
OUTPUT_DIR = "data_clean"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books.json")

# Règles de filtrage (identiques aux autres scripts)
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
    mot = re.sub(r'\(.*?\)', '', mot)   # supprime (ma), (bi)...
    mot = re.sub(r'^-|-$', '', mot)     # supprime tirets initiaux/finaux
    mot = mot.strip()
    return mot

def extraire_paires_depuis_texte(texte):
    """
    Cherche des lignes contenant un mot yipunu suivi d'une traduction française.
    Hypothèse : les PDF de type dictionnaire présentent souvent :
        mot_yipunu  :  traduction_française
        mot_yipunu  -  traduction_française
    On va capturer ces lignes avec une regex simple.
    """
    paires = {}
    # Pattern : début de ligne avec des lettres yipunu (on autorise certains diacritiques),
    # suivi d'un séparateur ( : , - , tabulation) et d'une traduction française.
    motif = re.compile(r'^([^\d\s]{1,30})\s*[:,\-]\s*(.{1,60})$', re.MULTILINE)
    for match in motif.finditer(texte):
        yipunu_raw = match.group(1).strip()
        francais_raw = match.group(2).strip()
        # Appliquer filtres
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

def traiter_pdf(chemin_pdf):
    try:
        reader = PdfReader(chemin_pdf)
        texte_complet = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texte_complet += page_text + "\n"
        paires = extraire_paires_depuis_texte(texte_complet)
        print(f"  -> {len(paires)} entrées extraites de {os.path.basename(chemin_pdf)}")
        return paires
    except Exception as e:
        print(f"Erreur lors du traitement de {chemin_pdf} : {e}")
        return {}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dictionnaire_global = {}
    for fichier in os.listdir(INPUT_DIR):
        if fichier.lower().endswith('.pdf'):
            chemin = os.path.join(INPUT_DIR, fichier)
            print(f"Analyse de {fichier}...")
            paires_fichier = traiter_pdf(chemin)
            for mot, traductions in paires_fichier.items():
                if mot not in dictionnaire_global:
                    dictionnaire_global[mot] = []
                for t in traductions:
                    if t not in dictionnaire_global[mot]:
                        dictionnaire_global[mot].append(t)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dictionnaire_global, f, ensure_ascii=False, indent=2)
    print(f"Total : {len(dictionnaire_global)} entrées sauvegardées dans {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
