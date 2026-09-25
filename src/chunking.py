import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import re
from src.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def découper_par_caracteres(texte: str, taille: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    """
    Découpe un texte selon un nombre de caractères fixe avec un chevauchement (overlap).
    """
    chunks = []
    debut = 0
    while debut < len(texte):
        fin = debut + taille
        chunk = texte[debut:fin]
        chunks.append(chunk)
        debut += taille - overlap
    return chunks

def découper_par_phrases(texte: str) -> list[str]:
    """
    Découpe un texte selon la ponctuation pour préserver la structure des phrases.
    """
    # Utilise une expression régulière pour couper aux points, points d'interrogation et d'exclamation
    phrases = re.split(r'(?<=[.!?]) +', texte)
    return [p.strip() for p in phrases if p.strip()]