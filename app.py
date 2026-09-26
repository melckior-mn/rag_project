import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from src.auth import afficher_interface_auth
from src.chat_history import charger_historique_chat, sauvegarder_message
from src.document_loader import extraire_texte_fichier
from src.pipeline import RAGPipeline

st.set_page_config(
    page_title="ChatBot RAG - Analyse Documentaire",
    page_icon="💬",
    layout="wide",
)
def appliquer_style_moderne():
  st.markdown(
      """
        <style>
        /* Import d'une police moderne */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Animation des conteneurs principaux */
        .main .block-container {
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
            max-width: 900px;
            padding-top: 2rem;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Animation d'apparition des messages */
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

        /* Personnalisation du panneau latéral (Sidebar) */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
            border-right: 1px solid rgba(0, 0, 0, 0.05);
        }

        /* Stylisation des boutons avec effet Pulse/Hover */
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

        /* Zone de saisie du chat stylisée */
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

        /* Animation pulse sur les badges d'état */
        .stAlert {
            border-radius: 12px;
            animation: pulse 2s infinite alternate;
        }

        </style>
    """,
      unsafe_allow_html=True,
  )
# 3. APPEL DE LA FONCTION POUR APPLIQUER LE STYLE
appliquer_style_moderne()

# 1. Vérification de l'authentification Supabase
est_connecte = afficher_interface_auth()

if not est_connecte:
  st.stop()  # Arrête l'exécution si l'utilisateur n'est pas connecté


# 2. Récupération de l'utilisateur connecté
user_id = st.session_state["user"].id
user_email = st.session_state["user"].email


@st.cache_resource
def charger_pipeline():
  return RAGPipeline()


pipeline = charger_pipeline()

st.title("💬 ChatBot RAG Multi-Documents")
st.caption(f"Espace de travail sécurisé de : `{user_email}`")

# 3. Initialisation et chargement de l'historique depuis Supabase
if "messages" not in st.session_state or st.session_state.get(
    "current_user_id"
) != user_id:
  st.session_state.messages = charger_historique_chat(user_id)
  st.session_state.current_user_id = user_id

# Barre latérale pour charger les fichiers
with st.sidebar:
  st.header("📂 Vos Documents")
  fichiers_uploadees = st.file_uploader(
      "Déposez vos fichiers (PDF, TXT, DOCX, XLSX)",
      type=["pdf", "txt", "docx", "xlsx"],
      accept_multiple_files=True,
  )

  # Bouton pour réinitialiser la conversation
  if st.button("🔄 Effacer la discussion"):
    st.session_state.messages = []
    # Optionnel: supprimer dans Supabase si nécessaire
    st.rerun()

# Extraction du texte
texte_global = ""
if fichiers_uploadees:
  textes = []
  for f in fichiers_uploadees:
    try:
      contenu = extraire_texte_fichier(f)
      textes.append(contenu)
    except Exception as e:
      st.error(f"Erreur {f.name} : {e}")
  texte_global = "\n\n".join(textes)
  st.sidebar.success(f"{len(fichiers_uploadees)} document(s) prêt(s)")

# Affichage de l'historique des messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])
    if "contexte" in message and message["contexte"]:
      with st.expander("🔍 Sources utilisées"):
        for idx, chunk in enumerate(message["contexte"], 1):
          st.info(f"**Extrait {idx} :** {chunk}")

# Zone de saisie du Chat
if question := st.chat_input("Posez votre question sur les documents..."):
  if not texte_global:
    st.warning(
        "Veuillez d'abord charger au moins un fichier dans la barre latérale."
    )
  else:
    # 1. Enregistrer et afficher la question
    st.session_state.messages.append({"role": "user", "content": question})
    sauvegarder_message(user_id, "user", question)

    with st.chat_message("user"):
      st.markdown(question)

    # 2. Générer et afficher la réponse du bot
    with st.chat_message("assistant"):
      with st.spinner("Analyse et recherche des réponses..."):
        resultat = pipeline.poser_question(
            question=question,
            texte_source=texte_global,
            user_id=user_id,  # Injection du user_id
            historique=st.session_state.messages[
                :-1
            ],  # exclut la question courante
        )

        st.markdown(resultat["reponse"])

        if resultat["contexte"]:
          with st.expander("🔍 Sources utilisées"):
            for idx, chunk in enumerate(resultat["contexte"], 1):
              st.info(f"**Extrait {idx} :** {chunk}")

        # Enregistrer la réponse dans la session et Supabase
        st.session_state.messages.append({
            "role": "assistant",
            "content": resultat["reponse"],
            "contexte": resultat["contexte"],
        })
        sauvegarder_message(user_id, "assistant", resultat["reponse"])