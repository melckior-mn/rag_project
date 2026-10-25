import io
from pathlib import Path
import sys
import uuid

sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from src.auth import afficher_interface_auth
from src.chat_history import (
    charger_conversations_utilisateur,
    charger_messages_session,
    sauvegarder_message,
)
from src.document_loader import extraire_texte_fichier
from src.pipeline import RAGPipeline
from src.storage import (
    lister_fichiers_utilisateur,
    supprimer_fichier_supabase,
    telecharger_texte_fichier_supabase,
    uploader_fichier_supabase,
)

st.set_page_config(
    page_title="ChatBot RAG",
    page_icon="🤖",
    layout="wide"
)


def appliquer_style_moderne():
  st.markdown(
      """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main .block-container {
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
            max-width: 900px;
            padding-top: 2rem;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        [data-testid="stChatMessage"] {
            border-radius: 16px;
            padding: 12px 18px;
            margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
            animation: popIn 0.4s ease-out forwards;
        }

        [data-testid="stChatMessage"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
        }

        @keyframes popIn {
            0% { opacity: 0; transform: scale(0.97); }
            100% { opacity: 1; transform: scale(1); }
        }

        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
            border-right: 1px solid rgba(0, 0, 0, 0.05);
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
            border: none;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
        }

        .stButton > button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4);
            color: white;
        }

        [data-testid="stChatInput"] {
            border-radius: 20px;
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: #6366f1;
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
        }

        .stAlert {
            border-radius: 12px;
            animation: pulse 2s infinite alternate;
        }
        </style>
    """,
      unsafe_allow_html=True,
  )


appliquer_style_moderne()

# 1. Authentification
est_connecte = afficher_interface_auth()

if not est_connecte:
  st.stop()

# 2. Utilisateur et Session
user_id = st.session_state["user"].id
user_email = st.session_state["user"].email

# Initialisation d'un identifiant de session unique
if "current_session_id" not in st.session_state:
  st.session_state.current_session_id = str(uuid.uuid4())


@st.cache_resource
def charger_pipeline():
  return RAGPipeline()


pipeline = charger_pipeline()

st.title("💬 ChatBot RAG Multi-Documents")
st.caption(f"Espace de travail sécurisé de : `{user_email}`")

# Chargement de la session active
if (
    "messages" not in st.session_state
    or st.session_state.get("current_user_id") != user_id
):
  st.session_state.messages = charger_messages_session(
      user_id, st.session_state.current_session_id
  )
  st.session_state.current_user_id = user_id

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
  # Bouton pour créer un nouveau chat
  if st.button("➕ Nouvelle discussion", use_container_width=True):
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

  st.markdown("---")
  st.header("📂 Vos Documents")
  fichiers_uploadees = st.file_uploader(
      "Déposez vos fichiers (PDF, TXT, DOCX, XLSX)",
      type=["pdf", "txt", "docx", "xlsx"],
      accept_multiple_files=True,
  )

  # Récupération de la liste des fichiers stockés pour cet utilisateur
  fichiers_stockes = lister_fichiers_utilisateur(user_id)

  if fichiers_stockes:
    st.markdown("**Fichiers enregistrés :**")
    for fichier in fichiers_stockes:
      nom_fichier = fichier.get("name")
      if nom_fichier and nom_fichier != ".emptyFolderPlaceholder":
        col_nom, col_suppr = st.columns([0.8, 0.2])
        with col_nom:
          st.text(f"📄 {nom_fichier}")
        with col_suppr:
          if st.button("❌", key=f"del_{nom_fichier}", help="Supprimer"):
            supprimer_fichier_supabase(user_id, nom_fichier)
            st.rerun()

  st.markdown("---")
  st.subheader("📜 Mes discussions")

  # Liste des conversations précédentes
  conversations = charger_conversations_utilisateur(user_id)
  for conv in conversations:
    est_active = conv["session_id"] == st.session_state.current_session_id
    prefixe = "💬 " if not est_active else "▶️ "

    if st.button(
        f"{prefixe}{conv['titre']}",
        key=conv["session_id"],
        use_container_width=True,
    ):
      st.session_state.current_session_id = conv["session_id"]
      st.session_state.messages = charger_messages_session(
          user_id, conv["session_id"]
      )
      st.rerun()

# Traitement des textes (depuis l'upload direct ou le stockage)
texte_global = ""
textes = []

# 1. Traitement direct des fichiers en cours d'upload dans le widget
if fichiers_uploadees:
  for f in fichiers_uploadees:
    try:
      uploader_fichier_supabase(user_id, f)
      f.seek(0)
      contenu = extraire_texte_fichier(f)
      textes.append(contenu)
    except Exception as e:
      st.error(f"Erreur traitement {f.name} : {e}")

# 2. Récupération des fichiers déjà enregistrés dans le stockage Supabase
if fichiers_stockes:
  for fichier in fichiers_stockes:
    nom_fichier = fichier.get("name")
    if nom_fichier and nom_fichier != ".emptyFolderPlaceholder":
      if not fichiers_uploadees or not any(
          f.name == nom_fichier for f in fichiers_uploadees
      ):
        file_bytes = telecharger_texte_fichier_supabase(user_id, nom_fichier)
        if file_bytes:
          file_obj = io.BytesIO(file_bytes)
          file_obj.name = nom_fichier
          try:
            contenu = extraire_texte_fichier(file_obj)
            textes.append(contenu)
          except Exception:
            pass

if textes:
  texte_global = "\n\n".join(textes)
  nb_total = len(textes)
  st.sidebar.success(f"{nb_total} document(s) actif(s)")

# Affichage des messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])
    if "contexte" in message and message["contexte"]:
      with st.expander("🔍 Sources utilisées"):
        for idx, chunk in enumerate(message["contexte"], 1):
          st.info(f"**Extrait {idx} :** {chunk}")

# Zone de saisie
if question := st.chat_input("Posez votre question sur les documents..."):
  if not texte_global:
    st.warning("Veuillez d'abord charger au moins un fichier dans la barre latérale.")
  else:
    # Enregistrement utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    sauvegarder_message(
        user_id, st.session_state.current_session_id, "user", question
    )

    with st.chat_message("user"):
      st.markdown(question)

    # Réponse de l'assistant
    with st.chat_message("assistant"):
      with st.spinner("Analyse et recherche des réponses..."):
        resultat = pipeline.poser_question(
            question=question,
            texte_source=texte_global,
            user_id=user_id,
            historique=st.session_state.messages[:-1],
        )

        st.write_stream(iter([resultat["reponse"]]))

        if resultat["contexte"]:
          with st.expander("🔍 Sources utilisées"):
            for idx, chunk in enumerate(resultat["contexte"], 1):
              st.info(f"**Extrait {idx} :** {chunk}")

        # Enregistrement assistant
        st.session_state.messages.append({
            "role": "assistant",
            "content": resultat["reponse"],
            "contexte": resultat["contexte"],
        })
        sauvegarder_message(
            user_id,
            st.session_state.current_session_id,
            "assistant",
            resultat["reponse"],
            resultat["contexte"],
        )

# Social links footer
social_icons_html = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  body { margin: 0; padding: 0; background-color: transparent; }
  .social-container { display: flex; justify-content: center; align-items: center; gap: 12px; padding: 10px 0; }
  .social-btn {
    width: 42px; height: 42px; background-color: #1a1a1e; border: 1px solid #2d2d35;
    border-radius: 10px; display: flex; justify-content: center; align-items: center;
    color: #a1a1aa; font-size: 18px; text-decoration: none; transition: all 0.3s ease-in-out;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  }
  .social-btn.github:hover { background-color: #24292e; color: #ffffff; box-shadow: 0 0 15px #ffffff; transform: translateY(-3px); }
  .social-btn.linkedin:hover { background-color: #0077b5; color: #ffffff; box-shadow: 0 0 15px #0077b5; transform: translateY(-3px); }
  .social-btn.facebook:hover { background-color: #1877f2; color: #ffffff; box-shadow: 0 0 15px #1877f2; transform: translateY(-3px); }
  .social-btn.whatsapp:hover { background-color: #25d366; color: #ffffff; box-shadow: 0 0 15px #25d366; transform: translateY(-3px); }
</style>
<div class="social-container">
  <a href="https://github.com/melckior-mn" target="_blank" class="social-btn github" title="GitHub"><i class="fab fa-github"></i></a>
  <a href="https://www.linkedin.com/in/melckior-tatch%C3%A9gnon-monnou-bb8a3a396/" target="_blank" class="social-btn linkedin" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
  <a href="https://web.facebook.com/mmelo2008" target="_blank" class="social-btn facebook" title="Facebook"><i class="fab fa-facebook-f"></i></a>
  <a href="https://wa.me/2290145582680" target="_blank" class="social-btn whatsapp" title="WhatsApp"><i class="fab fa-whatsapp"></i></a>
</div>
"""

with st.sidebar:
  st.markdown("---")
  st.markdown(
      "<p style='text-align: center; color: #71717a; font-size: 13px;"
      " margin-bottom: 5px;'>Mes réseaux & contact</p>",
      unsafe_allow_html=True,
  )
  st.components.v1.html(social_icons_html, height=65)
  st.markdown("""
        <div style="margin-top: -15px; margin-bottom: 20px;">
            <span style="font-size: 13px; color: #a1a1aa;">Développé par </span>
            <strong style="font-size: 14px; color: #6366f1;">Melckior MONNOU</strong>
        </div>
  """, unsafe_allow_html=True)
  st.markdown(
      """
        <div style="text-align: center; font-size: 11px; color: #a1a1aa; margin-top: 10px; line-height: 1.5;">
            <p style="margin-bottom: 4px;">© 2026 ChatBot RAG. Tous droits réservés.</p>
            <p>
                <a href="https://github.com/melckior-mn/rag_project/blob/main/TERMS.md" target="_blank" style="color: #6366f1; text-decoration: none;">CGU</a> • 
                <a href="https://github.com/melckior-mn/rag_project/blob/main/PRIVACY.md" target="_blank" style="color: #6366f1; text-decoration: none;">Confidentialité</a> • 
                <a href="https://opensource.org/licenses/MIT" target="_blank" style="color: #6366f1; text-decoration: none;">Licence MIT</a>
            </p>
        </div>
    """,
      unsafe_allow_html=True,
  )
  