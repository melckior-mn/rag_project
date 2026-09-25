import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.generator import GeminiGenerator

generator = GeminiGenerator()

contexte_test = [
    "La thermodynamique étude les transferts de chaleur.",
    "Le premier principe est la conservation de l'énergie."
]
question_test = "Que dit le premier principe ?"

reponse = generator.generer_reponse(question_test, contexte_test)
print("--- Réponse Gemini ---")
print(reponse)