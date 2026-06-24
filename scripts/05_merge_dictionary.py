import json
import os
from collections import OrderedDict

INPUT_DIR = "data_clean"
OUTPUT_FILE = "dictionnaire_yipunu_officiel.json"

def fusionner_dictionnaires(fichiers):
    dico_global = {}
    for fichier in fichiers:
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for mot, traductions in data.items():
                if mot not in dico_global:
                    dico_global[mot] = []
                for t in traductions:
                    if t not in dico_global[mot]:
                        dico_global[mot].append(t)
            print(f"Fusion de {os.path.basename(fichier)} : +{len(data)} entrées")
        except Exception as e:
            print(f"Erreur avec {fichier} : {e}")
    dico_trie = OrderedDict(sorted(dico_global.items(), key=lambda x: x[0].lower()))
    return dico_trie

def main():
    os.makedirs(INPUT_DIR, exist_ok=True)
    fichiers_json = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    if not fichiers_json:
        print("Aucun fichier JSON trouvé dans", INPUT_DIR)
        return
    dico_final = fusionner_dictionnaires(fichiers_json)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dico_final, f, ensure_ascii=False, indent=2)
    print(f"Dictionnaire final créé : {len(dico_final)} mots → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
