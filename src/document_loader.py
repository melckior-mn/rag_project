import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pypdf import PdfReader
import docx
import pandas as pd

def extraire_texte_fichier(uploaded_file) -> str:
    """
    Extrait le texte brut d'un fichier (.pdf, .txt, .docx, .xlsx).
    """
    nom_fichier = uploaded_file.name.lower()
    
    # 1. Fichier texte simple
    if nom_fichier.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
        
    # 2. Fichier PDF
    elif nom_fichier.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        texte_complet = []
        for page in reader.pages:
            texte_page = page.extract_text()
            if texte_page:
                texte_complet.append(texte_page)
        return "\n".join(texte_complet)
        
    # 3. Fichier Word (.docx)
    elif nom_fichier.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        paragraphes = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphes)
        
    # 4. Fichier Excel (.xlsx)
    elif nom_fichier.endswith(".xlsx"):
        # Lecture de toutes les feuilles du fichier Excel
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        lignes_texte = []
        
        for nom_feuille, df in excel_data.items():
            lignes_texte.append(f"--- Feuille : {nom_feuille} ---")
            # Nettoyage des colonnes et des valeurs
            df = df.dropna(how="all")
            for idx, row in df.iterrows():
                # Formate chaque ligne sous forme "Colonne1: Valeur1, Colonne2: Valeur2"
                ligne_str = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                if ligne_str:
                    lignes_texte.append(f"Ligne {idx + 1} -> {ligne_str}")
                    
        return "\n".join(lignes_texte)
        
    else:
        raise ValueError("Format non supporté. formats acceptés : .pdf, .txt, .docx, .xlsx")