import streamlit as st
from src.auth import get_supabase_client


def charger_historique_chat(user_id: str) -> list[dict]:
  """Charge l'historique des discussions de l'utilisateur depuis Supabase."""
  supabase = get_supabase_client()
  if not supabase:
    return []

  try:
    response = (
        supabase.table("chat_history")
        .select("role, content")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )

    # Formatage des messages pour Streamlit
    messages = []
    for record in response.data:
      messages.append({"role": record["role"], "content": record["content"]})
    return messages

  except Exception as e:
    st.error(f"Erreur lors du chargement de l'historique : {e}")
    return []


def sauvegarder_message(user_id: str, role: str, content: str):
  """Sauvegarde un nouveau message (utilisateur ou assistant) dans Supabase."""
  supabase = get_supabase_client()
  if not supabase:
    return

  try:
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "role": role,
        "content": content,
    }).execute()
  except Exception as e:
    st.error(f"Erreur lors de la sauvegarde du message : {e}")