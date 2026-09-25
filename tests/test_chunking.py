import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
# tests/test_chunking.py
from src.chunking import découper_par_caracteres, découper_par_phrases

texte_test = "La thermodynamique est la science de l'énergie. Elle étudie les transferts de chaleur. Le premier principe est la conservation."

print("--- Test par caractères ---")
print(découper_par_caracteres(texte_test, taille=40, overlap=10))

print("\n--- Test par phrases ---")
print(découper_par_phrases(texte_test))