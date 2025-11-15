import streamlit as st
from dotenv import load_dotenv

from agents.router import route_and_answer

# Chargement des variables d'environnement (.env)
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Assistant juridique (RAG)",
    page_icon="⚖️",
)

st.title("⚖️ Assistant juridique sur textes de loi (RAG + LLM)")
st.caption(
    "ℹ️ Cet assistant fournit des informations générales à partir de textes de loi "
    "(PDF fournis dans le projet). Il ne remplace pas un avocat ou un juriste."
)

# Mémoire de conversation
if "history" not in st.session_state:
    st.session_state["history"] = []

# Choix d'utilisation du RAG
use_rag = st.checkbox(
    "🔍 Utiliser les textes de loi (RAG)",
    value=True,
    help="Si coché, l'assistant cherche d'abord dans les PDF juridiques indexés.",
)

# Affichage de l'historique
for role, content in st.session_state["history"]:
    with st.chat_message(role):
        st.markdown(content)

# Saisie utilisateur
user_msg = st.chat_input(
    "Pose une question juridique (droits, obligations, articles, etc.)"
)

if user_msg:
    # On ajoute le message de l'utilisateur à l'historique
    st.session_state["history"].append(("user", user_msg))
    with st.chat_message("user"):
        st.markdown(user_msg)

        # On passe maintenant par le routeur d'agent
    answer, docs = route_and_answer(user_msg, use_rag=use_rag)
    st.session_state["history"].append(("assistant", answer))

    with st.chat_message("assistant"):
        st.markdown(answer)

        # Si des docs sont renvoyés → RAG juridique
        if docs:
            with st.expander("Voir les extraits de textes de loi utilisés"):
                for i, d in enumerate(docs, start=1):
                    st.markdown(f"**Extrait {i}** — {d.metadata}")
                    st.write(d.page_content[:600] + "…")

