import streamlit as st
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY


@st.cache_resource
def get_supabase_client():
  """Initialise et met en cache le client Supabase."""
  if not SUPABASE_URL or not SUPABASE_KEY:
    return None
  try:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
  except Exception:
    return None


def init_session_auth():
  if "user" not in st.session_state:
    st.session_state["user"] = None


def inscription(email: str, password: str):
  supabase = get_supabase_client()
  if not supabase:
    st.error(
        "Impossible de contacter Supabase. Vérifiez la configuration de"
        " SUPABASE_URL."
    )
    return
  try:
    response = supabase.auth.sign_up({"email": email, "password": password})
    if response.user:
      st.success("Compte créé ! Vous pouvez maintenant vous connecter.")
  except Exception as e:
    st.error(f"Échec de l'inscription : {e}")


def connexion(email: str, password: str):
  supabase = get_supabase_client()
  if not supabase:
    st.error(
        "Configuration Supabase invalide. Vérifiez l'URL dans votre fichier"
        " .env."
    )
    return
  try:
    response = supabase.auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    if response.user:
      st.session_state["user"] = response.user
      st.success("Connexion réussie !")
      st.rerun()
  except Exception:
    st.error("E-mail ou mot de passe incorrect.")


def deconnexion():
  supabase = get_supabase_client()
  if supabase:
    try:
      supabase.auth.sign_out()
    except Exception:
      pass
  st.session_state["user"] = None
  st.rerun()


def afficher_interface_auth():
  init_session_auth()

  if st.session_state["user"] is not None:
    user_email = st.session_state["user"].email
    st.sidebar.markdown(f"👤 **Connecté :** `{user_email}`")
    if st.sidebar.button("Se déconnecter"):
      deconnexion()
    return True
  else:
    st.title("🔐 Connexion au RAG Assistant")

    tab_login, tab_signup = st.tabs(["Se connecter", "Créer un compte"])

    with tab_login:
      with st.form("form_connexion"):
        email = st.text_input("Adresse e-mail")
        password = st.text_input("Mot de passe", type="password")
        submit_login = st.form_submit_button("Se connecter")

        if submit_login:
          if email and password:
            connexion(email, password)
          else:
            st.warning("Veuillez remplir tous les champs.")

    with tab_signup:
      with st.form("form_inscription"):
        new_email = st.text_input("Adresse e-mail")
        new_password = st.text_input("Mot de passe", type="password")
        submit_signup = st.form_submit_button("S'inscrire")

        if submit_signup:
          if new_email and new_password:
            inscription(new_email, new_password)
          else:
            st.warning("Veuillez remplir tous les champs.")

    return False