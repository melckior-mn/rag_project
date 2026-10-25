from openai import OpenAI
import streamlit as st
from src.auth import get_supabase_client


def generer_titre_intelligent(premier_message: str) -> str:
  """Génère un titre ultra-court via GPT-4o-mini."""
  try:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": (
                "Génère un titre ultra-court (3 à 4 mots maximum, sans"
                " guillemets, sans ponctuation) pour résumer ce message :"
                f" '{premier_message}'"
            ),
        }],
        max_tokens=15,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
  except Exception:
    return (
        premier_message[:20] + "..."
        if len(premier_message) > 20
        else premier_message
    )


def charger_conversations_utilisateur(user_id: str) -> list[dict]:
  """Récupère la liste des conversations uniques avec leur titre intelligent."""
  supabase = get_supabase_client()
  if not supabase:
    return []

  try:
    # Récupération de tous les messages de l'utilisateur ordonnés par date de création
    res = (
        supabase.table("chat_history")
        .select("session_id, created_at, content, title")
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

      # Si la session n'est pas encore enregistrée dans notre dictionnaire
      if s_id not in sessions_dict:
        # On priorise un champ 'title' non vide, sinon on génère dynamiquement si manquant
        titre = row.get("title")
        if not titre:
          titre = generer_titre_intelligent(row["content"])
          # On met à jour la ligne en base de données pour ne plus ré-appeler l'API pour cette session
          try:
            supabase.table("chat_history").update({"title": titre}).eq(
                "session_id", s_id
            ).execute()
          except Exception:
            pass

        sessions_dict[s_id] = {
            "session_id": s_id,
            "titre": titre,
            "created_at": row.get("created_at"),
        }

    # Tri de la liste des conversations de la plus récente à la plus ancienne
    liste_sessions = list(sessions_dict.values())
    liste_sessions.sort(key=lambda x: x["created_at"], reverse=True)

    return liste_sessions
  except Exception:
    return []


def charger_messages_session(user_id: str, session_id: str) -> list[dict]:
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
  """Sauvegarde le message dans Supabase."""
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

    # Si c'est le premier message de l'utilisateur dans cette session, on génère le titre
    if role == "user":
      check_first = (
          supabase.table("chat_history")
          .select("id")
          .eq("session_id", session_id)
          .execute()
      )
      if not check_first.data:
        payload["title"] = generer_titre_intelligent(content)

    supabase.table("chat_history").insert(payload).execute()
  except Exception:
    pass