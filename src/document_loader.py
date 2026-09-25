import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pypdf import PdfReader

def extraire_texte_fichier(uploaded_file) -> str:
    """
    Extrait le texte brut à partir d'un fichier téléversé dans Streamlit (.pdf ou .txt).
    """
    nom_fichier = uploaded_file.name.lower()
    
    # Cas 1 : Fichier texte simple
    if nom_fichier.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
        
    # Cas 2 : Fichier PDF
    elif nom_fichier.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        texte_complet = []
        for page in reader.pages:
            texte_page = page.extract_text()
            if texte_page:
                texte_complet.append(texte_page)
        return "\n".join(texte_complet)
        
    else:
        raise ValueError("Format de fichier non supporté. Veuillez utiliser un fichier .txt ou .pdf.")