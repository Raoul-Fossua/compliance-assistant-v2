import os

from langchain_community.document_loaders import PyPDFium2Loader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

DATA_DIR = "./data"
DB_DIR = "./chroma_db"


def load_all_pdfs():
    docs = []
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"[WARN] Le dossier {DATA_DIR} vient d'être créé. Ajoute-y des PDFs.")
        return docs

    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".pdf"):
            path = os.path.join(DATA_DIR, file)
            print(f"[LOAD] {path}")
            loader = PyPDFium2Loader(path)
            docs.extend(loader.load())

    return docs


def build_vectorstore():
    print("[INFO] Chargement des PDFs de lois dans data/ ...")
    docs = load_all_pdfs()
    print(f"[INFO] Nombre de pages/documents chargés : {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)
    print(f"[INFO] Nombre de chunks après découpage : {len(chunks)}")

    # 💡 EMBEDDINGS 100% GRATUITS, AUCUN APPEL OPENAI
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR,
    )

    vectordb.persist()
    print("[OK] Index juridique (Chroma) construit/mis à jour.")
    return vectordb


if __name__ == "__main__":
    build_vectorstore()
