import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.pipeline import RAGPipeline

# Instanciation du pipeline complet
rag = RAGPipeline()

# Un texte brut plus complet
texte_document = """
La thermodynamique est la branche de la physique qui étudie les relations entre la chaleur, le travail et l'énergie.
Le premier principe de la thermodynamique affirme que l'énergie globale d'un système isolé est conservée.
Le deuxième principe introduit la notion d'entropie, indiquant que le désordre d'un système ne peut qu meugmenter ou rester constant.
En informatique, Python est un langage de programmation interprété très utilisé en intelligence artificielle.
"""

question = "Que dit le deuxième principe de la thermodynamique ?"

# Lancement du RAG
resultat = rag.poser_question(question=question, texte_source=texte_document)

print("--- RÉPONSET ---")
print(resultat["reponse"])
print("\n--- CONTEXTE UTILISÉ ---")
for doc in resultat["contexte"]:
    print(f"- {doc}")