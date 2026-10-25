import streamlit as st
from src.auth import get_supabase_client


def charger_conversations_utilisateur(user_id: str) -> list[dict]:
  """Récupère la liste des conversations uniques de l'utilisateur."""
  supabase = get_supabase_client()
  if not supabase:
    return []

  try:
    res = (
        supabase.table("chat_history")
        .select("session_id, created_at, content")
        .eq("user_id", user_id)
        .eq("role", "user")
        .order("created_at", desc=False)
        .execute()
    )

    sessions_dict = {}

    for row in res.data:
      s_id = row.get("session_id")
      if not s_id:
        continue

      # On garde la première occurrence (premier message) pour nommer la session
      if s_id not in sessions_dict:
        content = row.get("content", "")
        titre = content[:25] + "..." if len(content) > 25 else content
        sessions_dict[s_id] = {
            "session_id": s_id,
            "titre": titre,
            "created_at": row.get("created_at"),
        }

    # Tri de la plus récente à la plus ancienne
    liste_sessions = list(sessions_dict.values())
    liste_sessions.sort(key=lambda x: x["created_at"], reverse=True)

    return liste_sessions
  except Exception:
    return []


def charger_messages_session(user_id: str, session_id: str) -> list[dict]:
  """Charge l'historique complet d'une session spécifique."""
  supabase = get_supabase_client()
  if not supabase:
    return []

  try:
    res = (
        supabase.table("chat_history")
        .select("role, content, context")
        .eq("user_id", user_id)
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .execute()
    )
    return res.data or []
  except Exception:
    return []


def sauvegarder_message(
    user_id: str,
    session_id: str,
    role: str,
    content: str,
    context: list = None,
):
  """Sauvegarde un message dans Supabase."""
  supabase = get_supabase_client()
  if not supabase:
    return

  try:
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "context": context or [],
    }
    supabase.table("chat_history").insert(payload).execute()
  except Exception:
    pass