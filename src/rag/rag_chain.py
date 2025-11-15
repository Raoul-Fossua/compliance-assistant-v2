from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline

DB_DIR = "./chroma_db"

# Modèle HuggingFace pour générer la réponse (LLM local via HF Hub)
# La première exécution téléchargera le modèle.
llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectordb = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings,
    )
    return vectordb


def answer_with_rag(question: str, k: int = 4):
    """
    Récupère des extraits pertinents dans les PDF juridiques (Chroma + HF embeddings),
    puis demande au modèle HuggingFace de synthétiser une réponse à partir du contexte.
    """
    vectordb = get_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": k})

    try:
        docs = retriever.invoke(question)
    except Exception as e:
        print(f"[ERROR] Retrieval failed: {e}")
        docs = []

    if not docs:
        return (
            "Je n'ai trouvé aucun extrait pertinent dans les textes de loi fournis.",
            []
        )

    # Construire le contexte à partir des PDF
    context = "\n\n".join(
        [f"[EXTRAIT {i+1}]\n{d.page_content}" for i, d in enumerate(docs)]
    )

    prompt = (
        "Tu es un assistant juridique pédagogique français. "
        "Tu réponds de manière synthétique en t'appuyant UNIQUEMENT sur le contexte fourni, "
        "qui provient de textes de loi (Code du travail, Code civil, supports de cours). "
        "Si une information n'apparaît pas dans le contexte, tu expliques que tu ne peux pas la garantir.\n\n"
        f"CONTEXTE :\n{context}\n\n"
        f"QUESTION : {question}\n\n"
        "RÉPONSE :"
    )

    # Appel au modèle HuggingFace
    result = llm(
        prompt,
        max_new_tokens=400,
        num_return_sequences=1
    )[0]["generated_text"]

    return result, docs
