from google import genai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder
from sentence_transformers import util


# ============================================================
# 1. Initialisation
# ============================================================

load_dotenv()

client = genai.Client()

model = SentenceTransformer("all-MiniLM-L6-v2")

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


# ============================================================
# 2. Documents
# ============================================================

documents = [
    "La thermodynamique est une branche de la physique qui étudie les transformations de l'énergie et les échanges de chaleur.",
    "La première loi de la thermodynamique exprime la conservation de l'énergie.",
    "Elle établit une relation entre la chaleur, le travail et la variation d'énergie interne.",
    "La deuxième loi de la thermodynamique introduit la notion d'entropie.",
    "Elle permet notamment de déterminer le sens d'évolution de certaines transformations.",
    "L'entropie est une grandeur physique importante en thermodynamique.",
    "Elle intervient dans l'étude des processus irréversibles."
]


# ============================================================
# 3. Création des chunks
# ============================================================

taille_chunk = 3
overlap = 1

chunks = []

debut = 0

while debut < len(documents):

    fin = debut + taille_chunk

    chunk = " ".join(documents[debut:fin])

    chunks.append(chunk)

    debut += taille_chunk - overlap


# ============================================================
# 4. Embeddings des chunks
# ============================================================

embeddings_chunks = model.encode(
    chunks,
    convert_to_tensor=True
)


# ============================================================
# 5. Fonction de retrieval
# ============================================================

def retrieve(question, chunks, embeddings_chunks, k=3, n=2):

    # Encoder la question
    embedding_question = model.encode(
        question,
        convert_to_tensor=True
    )

    # Similarité question ↔ chunks
    scores_embedding = util.cos_sim(
        embedding_question,
        embeddings_chunks
    )[0]

    # Top-K candidats
    indices = scores_embedding.argsort(
        descending=True
    )[:k]

    # Préparer les paires pour le Cross-Encoder
    paires = [
        [question, chunks[index]]
        for index in indices
    ]

    # Reranking
    scores_cross = reranker.predict(paires)

    # Classement final
    classement = sorted(
        zip(indices, scores_cross),
        key=lambda x: x[1],
        reverse=True
    )

    # Garder les N meilleurs
    resultats = []

    for index, score in classement[:n]:

        resultats.append({
            "chunk": chunks[index],
            "score": float(score)
        })

    return resultats


# ============================================================
# 6. Question utilisateur
# ============================================================

question = "Comment fonctionne une batterie ?"

# ============================================================
# 7. Retrieval
# ============================================================

resultats = retrieve(
    question,
    chunks,
    embeddings_chunks,
    k=3,
    n=2
)


# ============================================================
# 8. Construction automatique du contexte
# ============================================================

contexte = "\n\n".join(
    resultat["chunk"]
    for resultat in resultats
)


# ============================================================
# 9. Création du prompt
# ============================================================

prompt = f"""
Tu es un assistant qui répond uniquement à partir du contexte fourni.

CONTEXTE :
{contexte}

QUESTION :
{question}

RÈGLES :
- Réponds uniquement à partir du contexte.
- N'utilise pas de connaissances extérieures.
- Si la réponse n'est pas présente dans le contexte,
  indique que l'information n'est pas présente dans les documents.
"""


# ============================================================
# 10. Génération avec Gemini
# ============================================================

response = client.interactions.create(
    model="gemini-3.6-flash",
    input=prompt
)


# ============================================================
# 11. Affichage
# ============================================================

print("\n===== CONTEXTE RÉCUPÉRÉ =====\n")
print(contexte)

print("\n===== RÉPONSE =====\n")
print(response.output_text)