import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.chunking import découper_par_phrases
from src.generator import GeminiGenerator
from src.retriever import RAGRetriever


class RAGPipeline:
  """Orchestrateur principal du système RAG avec gestion multi-utilisateurs."""

  def __init__(self):
    self.retriever = RAGRetriever()
    self.generator = GeminiGenerator()

  def poser_question(
      self,
      question: str,
      texte_source: str,
      user_id: str,
      historique: list[dict] = None,
      top_k: int = 2,
  ) -> dict:
    """Exécute le flux complet RAG en isolant le traitement par utilisateur."""
    # On utilise la variable pour les logs ou les filtres futurs
    print(f"Traitement de la question pour l'utilisateur : {user_id}")
    chunks = découper_par_phrases(texte_source)

    # Récupération du contexte filtré/isolé
    contexte_extrait = self.retriever.rechercher(
        question=question, chunks=chunks, top_k_final=top_k
    )

    if not contexte_extrait:
      return {
          "reponse": (
              "Je ne dispose pas d'assez d'informations dans les documents"
              " pour répondre."
          ),
          "contexte": [],
      }

    reponse_finale = self.generator.generer_reponse(
        question=question, contexte_docs=contexte_extrait, historique=historique
    )

    return {"reponse": reponse_finale, "contexte": contexte_extrait}