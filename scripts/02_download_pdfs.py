import requests
import os

# ============================================================
# Sources PDF confirmées
# ============================================================
PDF_URLS = {
    # Parlons Yipunu (livre complet, ~3000 mots)
    "parlons_yipunu.pdf": (
        "https://theswissbay.ch/pdf/Books/Linguistics/Mega%20linguistics%20pack/"
        "African/Niger-Congo/Bantu/Punu%3B%20Parlons%20yipunu.pdf"
    ),

    # Thèse de Tomba Diogo (SRC_03) – URL exacte fournie
    "these_tomba_diogo.pdf": (
        "https://theses.hal.science/tel-01368245v1/file/"
        "TOMBA_DIOGO_Amevi_Christine_Cerena_vavd.pdf"
    ),

    # Dictionnaire Punu sur Scribd (SRC_06 selon votre tableau)
    # ATTENTION : Scribd ne permet pas le téléchargement direct sans authentification.
    # Cette URL est un placeholder ; le téléchargement échouera probablement.
    # Vous pouvez plus tard remplacer par un autre scraper ou ignorer cette source.
    "scribd_dictionnaire_punu.pdf": "https://scribd.com/document/123456789/Dictionnaire-Punu"
}

OUTPUT_DIR = "data_raw"

def download_pdf(filename, url):
    try:
        print(f"Téléchargement de {filename} depuis {url}...")
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"✅ Téléchargé : {filename}")
    except Exception as e:
        print(f"❌ Échec du téléchargement de {filename} : {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename, url in PDF_URLS.items():
        # Ne pas retélécharger si le fichier existe déjà (évite de surcharger les serveurs)
        if not os.path.exists(os.path.join(OUTPUT_DIR, filename)):
            download_pdf(filename, url)
        else:
            print(f"ℹ️ Déjà présent : {filename}")

if __name__ == "__main__":
    main()
