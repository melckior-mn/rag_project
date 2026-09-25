import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Lecture de la clé API (Streamlit Secrets pour le Cloud, .env pour le local)
try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL_NAME = "gemini-2.5-flash"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Paramètres du découpage (Chunking)
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50