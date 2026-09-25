import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.retriever import RAGRetriever

retriever = RAGRetriever()

corpus_test = [
    "Python est un langage de programmation très populaire pour la Data Science.",
    "La thermodynamique étudie les transferts de chaleur et d'énergie.",
    "Le premier principe de la thermodynamique concerne la conservation de l'énergie.",
    "Java est un autre langage utilisé en entreprise pour le backend."
]

question = "Qu'est-ce que le premier principe ?"

resultats = retriever.rechercher(question, corpus_test, top_k_bi=3, top_k_final=1)

print("--- Résultat de la recherche ---")
print(resultats)