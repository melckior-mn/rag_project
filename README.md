# 🤖 ChatBot RAG Multi-Documents

Un chatbot intelligent basé sur le RAG (Retrieval-Augmented Generation) permettant d'interroger vos propres documents (PDF, TXT, DOCX, XLSX) de manière sécurisée.

## 🚀 Fonctionnalités
- **RAG Multi-Documents** : Importez vos fichiers et discutez avec leur contenu via GPT-4o-mini.
- **Sécurité et Authentification** : Gestion des utilisateurs et isolation totale des données (RLS) via **Supabase**.
- **Historique des sessions** : Sauvegarde automatique des discussions et navigation multi-sessions.
- **Interface Moderne** : Développé avec **Streamlit**.

## 🛠️ Stack Technique
- **Frontend / UI** : Streamlit
- **Backend / DB / Auth / Storage** : Supabase
- **IA / LLM** : gemini-3.5-flash

## 📦 Installation en local

1. Clonez le dépôt :
   ```bash
   git clone [https://github.com/melckior-mn/rag_project.git](https://github.com/melckior-mn/rag_project.git)
   cd rag_project
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
3. Créez un fichier .env à la racine et configurez vos clés :
   ```bash
   SUPABASE_URL="votre_url_supabase"
   SUPABASE_KEY="votre_cle_supabase"
   OPENAI_API_KEY="votre_cle_openai"
4. Lancez l'application :
   ```bash
   streamlit run app.py

Une fois le fichier créé en local, il vous suffira de faire un dernier petit `git push` pour l'ajouter proprement sur votre GitHub !

📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
