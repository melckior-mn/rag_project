import streamlit as st
from supabase import Client, create_client
from src.config import SUPABASE_KEY, SUPABASE_URL


def get_supabase_client() -> Client:
  if not SUPABASE_URL or not SUPABASE_KEY:
    st.error(
        "Les identifiants Supabase ne sont pas configurés dans le fichier"
        " .env."
    )
    return None
  return create_client(SUPABASE_URL, SUPABASE_KEY)


def afficher_interface_auth() -> bool:
  """Affiche une interface d'authentification native, stable et fonctionnelle."""

  # 1. Gestion de la session utilisateur
  if "user" in st.session_state and st.session_state["user"] is not None:
    with st.sidebar:
      st.markdown(f"👤 **Connecté :** `{st.session_state['user'].email}`")
      if st.button("Se déconnecter", use_container_width=True):
        st.session_state["user"] = None
        st.session_state.messages = []
        st.rerun()
    return True

  # 2. Centrage du formulaire
  _, col_center, _ = st.columns([1, 2, 1])

  with col_center:
    st.markdown(
        "<h2 style='text-align: center; font-weight: 700;'>ChatBot RAG</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #a1a1aa; font-size: 14px;"
        " margin-bottom: 20px;'>Connectez-vous pour accéder à vos"
        " documents.</p>",
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(
        ["🔑 Se connecter", "📝 Créer un compte"]
    )

    # --- CONNEXION ---
    with tab_login:
      with st.form("form_connexion", clear_on_submit=False):
        email = st.text_input(
            "Adresse e-mail",
            placeholder="votre.email@exemple.com",
            key="login_email",
        )
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )
        btn_connexion = st.form_submit_button(
            "Se connecter", use_container_width=True, type="primary"
        )

        if btn_connexion:
          if email and password:
            supabase = get_supabase_client()
            if supabase:
              try:
                res = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                st.session_state["user"] = res.user
                st.success("Connexion réussie !")
                st.rerun()
              except Exception as e:
                st.error(f"Erreur de connexion : {e}")
          else:
            st.warning("Veuillez remplir tous les champs.")

    # --- INSCRIPTION ---
    with tab_signup:
      with st.form("form_inscription", clear_on_submit=False):
        email = st.text_input(
            "Adresse e-mail",
            placeholder="votre.email@exemple.com",
            key="signup_email",
        )
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="••••••••",
            key="signup_password",
        )
        btn_inscription = st.form_submit_button(
            "S'inscrire", use_container_width=True, type="primary"
        )

        if btn_inscription:
          if email and password:
            supabase = get_supabase_client()
            if supabase:
              try:
                res = supabase.auth.sign_up(
                    {"email": email, "password": password}
                )
                st.session_state["user"] = res.user
                st.success("Compte créé avec succès !")
                st.rerun()
              except Exception as e:
                st.error(f"Erreur d'inscription : {e}")
          else:
            st.warning("Veuillez remplir tous les champs.")

  return False