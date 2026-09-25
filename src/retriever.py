import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sentence_transformers import SentenceTransformer, CrossEncoder, util
from src.config import EMBEDDING_MODEL_NAME, RERANKER_MODEL_NAME

class RAGRetriever:
    """
    Classe gérant la recherche d'information (Retrieval + Re-ranking).
    """
    def __init__(self):
        # Chargement du modèle d'embeddings (Bi-Encoder)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        # Chargement du modèle de Re-ranking (Cross-Encoder)
        self.reranker_model = CrossEncoder(RERANKER_MODEL_NAME)

    def rechercher(self, question: str, chunks: list[str], top_k_bi: int = 5, top_k_final: int = 2) -> list[str]:
        """
        Effectue la recherche vectorielle puis affine avec le Cross-Encoder.
        """
        if not chunks:
            return []

        # --- ÉAPE 1 : Bi-Encoder (Filtrage rapide) ---
        # Vectorisation de la question et des chunks
        question_embedding = self.embedding_model.encode(question, convert_to_tensor=True)
        chunks_embeddings = self.embedding_model.encode(chunks, convert_to_tensor=True)

        # Calcul des scores de similarité cosinus
        scores_cos = util.cos_sim(question_embedding, chunks_embeddings)[0]

        # Récupération des indices des top_k_bi meilleurs candidats
        top_indices = scores_cos.argsort(descending=True)[:top_k_bi].tolist()
        candidats = [chunks[i] for i in top_indices]

        # --- ÉAPE 2 : Cross-Encoder (Re-ranking de précision) ---
        # Préparation des paires (question, candidat)
        paires = [[question, doc] for doc in candidats]
        
        # Calcul des scores de pertinence fins
        scores_cross = self.reranker_model.predict(paires)

        # Tri des candidats selon le score du Cross-Encoder
        candidats_avec_scores = list(zip(candidats, scores_cross))
        candidats_avec_scores.sort(key=lambda x: x[1], reverse=True)

        # Retourne uniquement les top_k_final meilleurs documents
        documents_finaux = [doc for doc, score in candidats_avec_scores[:top_k_final]]
        return documents_finaux