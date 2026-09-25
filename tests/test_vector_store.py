import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.vector_store import VectorStoreManager

# Initialisation
vector_store = VectorStoreManager()

# Corpus de test
mots_cles = [
    "La thermodynamique étudie les transferts de chaleur.",
    "Python est un langage de programmation puissant.",
    "Le premier principe concerne la conservation de l'énergie."
]

# Ajout à la base vectorielle
vector_store.ajouter_documents(mots_cles)

# Recherche
resultats = vector_store.chercher_similaires("Qu'est-ce que Python ?", n_results=1)

print("--- Résultat de ChromaDB ---")
print(resultats)