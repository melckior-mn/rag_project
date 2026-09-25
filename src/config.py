import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Clé API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configuration des Modèles
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GEMINI_MODEL_NAME = "gemini-3.6-flash"

# Hyperparamètres de Chunking
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50