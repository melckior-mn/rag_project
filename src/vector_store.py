import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.utils import embedding_functions
from src.config import BASE_DIR, EMBEDDING_MODEL_NAME

class VectorStoreManager:
    """
    Gère la base de données vectorielle ChromaDB sur le disque.
    """
    def __init__(self, collection_name: str = "rag_documents"):
        # 1. Chemin vers le stockage local
        self.db_path = BASE_DIR / "chroma_db"
        
        # 2. Utilisation explicite du modèle SentenceTransformer
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        # 3. Initialisation du client persistent
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # 4. Création ou récupération de la collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def ajouter_documents(self, chunks: list[str], ids: list[str] = None):
        """
        Stocke les chunks dans la base vectorielle.
        """
        if not chunks:
            return

        if ids is None:
            # Génération d'IDs uniques basés sur l'index
            ids = [f"doc_{i}" for i in range(len(chunks))]

        self.collection.add(
            documents=chunks,
            ids=ids
        )

    def chercher_similaires(self, question: str, n_results: int = 5) -> list[str]:
        """
        Recherche les chunks les plus proches vectoriellement de la question.
        """
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        return []