import streamlit as st
from src.auth import get_supabase_client


def uploader_fichier_supabase(user_id: str, uploaded_file) -> str:
  """Téléverse un fichier dans le Storage de Supabase sous un dossier utilisateur."""
  supabase = get_supabase_client()
  if not supabase:
    return None

  try:
    # Chemin unique du fichier : user_id/nom_du_fichier
    file_path = f"{user_id}/{uploaded_file.name}"

    # Lecture des octets du fichier
    file_bytes = uploaded_file.getvalue()

    # Upload vers le bucket 'documents' (upsert=True pour remplacer si le nom existe déjà)
    supabase.storage.from_("documents").upload(
        path=file_path, file=file_bytes, file_options={"upsert": "true"}
    )

    return file_path
  except Exception as e:
    # Si le fichier existe déjà, l'upload peut renvoyer une erreur selon la config, on gère l'upsert
    return f"{user_id}/{uploaded_file.name}"


def lister_fichiers_utilisateur(user_id: str) -> list:
  """Liste tous les fichiers stockés pour l'utilisateur connecté."""
  supabase = get_supabase_client()
  if not supabase:
    return []

  try:
    # Liste les fichiers dans le dossier personnel de l'utilisateur
    response = supabase.storage.from_("documents").list(f"{user_id}")
    return response or []
  except Exception as e:
    return []


def telecharger_texte_fichier_supabase(user_id: str, file_name: str) -> bytes:
  """Télécharge les octets d'un fichier depuis Supabase Storage."""
  supabase = get_supabase_client()
  if not supabase:
    return None

  try:
    file_path = f"{user_id}/{file_name}"
    response = supabase.storage.from_("documents").download(file_path)
    return response
  except Exception as e:
    st.error(f"Erreur lors du téléchargement du fichier : {e}")
    return None


def supprimer_fichier_supabase(user_id: str, file_name: str):
  """Supprime un fichier du Storage Supabase."""
  supabase = get_supabase_client()
  if not supabase:
    return

  try:
    file_path = f"{user_id}/{file_name}"
    supabase.storage.from_("documents").remove([file_path])
  except Exception as e:
    st.error(f"Erreur lors de la suppression : {e}")