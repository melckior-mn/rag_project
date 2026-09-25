import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from google import genai
from src.config import GEMINI_MODEL_NAME

class GeminiGenerator:
    """
    Classe responsable de la génération de réponses via l'API Gemini avec support de l'historique.
    """
    def __init__(self):
        self.client = genai.Client()
        self.model_name = GEMINI_MODEL_NAME

    def generer_reponse(self, question: str, contexte_docs: list[str], historique: list[dict] = None) -> str:
        """
        Formate le prompt RAG avec contexte et historique conversationnel.
        """
        contexte_texte = "\n\n".join([f"- {doc}" for doc in contexte_docs])
        
        # Formater l'historique des échanges sous forme de texte
        historique_texte = ""
        if historique:
            historique_texte = "HISTORIQUE DE LA CONVERSATION :\n"
            for msg in historique[-4:]:  # On ne garde que les 4 derniers messages pour ne pas saturer le prompt
                role = "Utilisateur" if msg["role"] == "user" else "Assistant"
                historique_texte += f"{role} : {msg['content']}\n"
            historique_texte += "\n"

        prompt = f"""Tu es un assistant virtuel basé sur des documents. 
Réponds à la question posée en t'appuyant EXCLUSIVEMENT sur le contexte fourni ci-dessous.
Prends en compte l'historique de la conversation pour comprendre le contexte des répliques précédentes.
Si l'information n'est pas présente dans le contexte, réponds simplement que tu ne sais pas.

{historique_texte}CONTEXTE DOCS :
{contexte_texte}

QUESTION ACTUELLE :
{question}
"""

        interaction = self.client.interactions.create(
            model=self.model_name,
            input=prompt
        )

        return interaction.output_text