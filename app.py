import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from src.pipeline import RAGPipeline
from src.document_loader import extraire_texte_fichier

st.set_page_config(
    page_title="ChatBot RAG - Analyse Documentaire",
    page_icon="💬",
    layout="wide"
)

@st.cache_resource
def charger_pipeline():
    return RAGPipeline()

st.title("💬 ChatBot RAG Multi-Documents")
st.write("Discutez en direct avec vos documents !")

pipeline = charger_pipeline()

# Initialisation de la mémoire de discussion dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Barre latérale pour charger les fichiers
with st.sidebar:
    st.header("📂 Vos Documents")
    fichiers_uploadees = st.file_uploader(
        "Déposez vos fichiers (PDF, TXT, DOCX, XLSX)",
        type=["pdf", "txt", "docx", "xlsx"],
        accept_multiple_files=True
    )
    
    # Bouton pour réinitialiser la conversation
    if st.button("🔄 Effacer la discussion"):
        st.session_state.messages = []
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

# Affichage de l'historique des messages dans l'IHM
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
        st.warning("Veuillez d'abord charger au moins un fichier dans la barre latérale.")
    else:
        # 1. Afficher le message de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # 2. Générer et afficher la réponse du bot
        with st.chat_message("assistant"):
            with st.spinner("Analyse et recherche des réponses..."):
                # Appel du pipeline RAG en transmettant l'historique
                resultat = pipeline.poser_question(
                    question=question, 
                    texte_source=texte_global,
                    historique=st.session_state.messages[:-1] # exclut la question courante
                )

                st.markdown(resultat["reponse"])
                
                if resultat["contexte"]:
                    with st.expander("🔍 Sources utilisées"):
                        for idx, chunk in enumerate(resultat["contexte"], 1):
                            st.info(f"**Extrait {idx} :** {chunk}")

                # Enregistrer la réponse dans la mémoire de la session
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": resultat["reponse"],
                    "contexte": resultat["contexte"]
                })

