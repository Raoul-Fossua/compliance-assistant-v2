"""
Application Streamlit pour l'assistant de conformité commerciale
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv

# ============================================================================
# AJOUT DES CHEMINS PYTHON
# ============================================================================
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Chargement des variables d'environnement
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

# ============================================================================
# IMPORTS
# ============================================================================
from agents.router import route_and_answer, get_router
from tools import get_tools_instance
from tools.rag_tool import get_rag_tool
from tools.judilibre_tool import get_judilibre_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# INITIALISATION OBLIGATOIRE DE SESSION STATE
# ============================================================================

def init_session_state():
    """Initialise toutes les variables de session - À APPELER AU DÉBUT"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "use_rag" not in st.session_state:
        st.session_state.use_rag = True
    if "use_jurisprudence" not in st.session_state:
        st.session_state.use_jurisprudence = True
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "queries_count": 0,
            "rag_queries": 0,
            "citation_resolutions": 0,
            "avg_response_time": 0
        }
    if "tools_initialized" not in st.session_state:
        st.session_state.tools_initialized = False

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="Assistant de Conformité Commerciale",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ⚠️ CRITICAL : Initialiser Session State AVANT toute utilisation
init_session_state()

# ============================================================================
# STYLES CSS
# ============================================================================

st.markdown("""
<style>
    .citation {
        background-color: #f0f2f6;
        border-left: 4px solid #ff4b4b;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .threshold-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ffa500;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .threshold-success {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .metadata {
        font-size: 0.8em;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("⚖️ Conformité Commerciale")
    st.caption("Assistant basé sur le Code de commerce")
    st.divider()
    
    st.subheader("⚙️ Configuration")
    # Maintenant st.session_state.use_rag existe grâce à init_session_state()
    st.session_state.use_rag = st.toggle("🔍 Recherche RAG", value=st.session_state.use_rag)
    st.session_state.use_jurisprudence = st.toggle("⚖️ Jurisprudence", value=st.session_state.use_jurisprudence)
    st.session_state.show_sources = st.toggle("📚 Afficher les sources", value=st.session_state.show_sources)
    
    st.divider()
    
    st.subheader("📊 Statistiques")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Requêtes", st.session_state.stats["queries_count"])
    with col2:
        st.metric("Temps moy.", f"{st.session_state.stats['avg_response_time']:.0f}ms")
    
    st.divider()
    
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================================
# CORPS PRINCIPAL
# ============================================================================

# Initialisation des outils (une seule fois)
if not st.session_state.tools_initialized:
    with st.spinner("🔧 Initialisation des outils..."):
        try:
            st.session_state.router = get_router()
            st.session_state.tools = get_tools_instance()
            st.session_state.rag_tool = get_rag_tool()
            st.session_state.judilibre = get_judilibre_tool()
            st.session_state.tools_initialized = True
            st.success("✅ Outils initialisés")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
            st.session_state.tools_initialized = False

st.title("⚖️ Assistant de Conformité Commerciale")
st.caption("Recherche intelligente dans le Code de commerce | Jurisprudence | Vérification de seuils")

# Message d'accueil
if not st.session_state.messages:
    welcome = """
    Bonjour ! Je suis votre assistant de conformité commerciale. 🤖
    
    **Exemples de questions :**
    - Que dit l'article L.225-102-4 ?
    - Une entreprise avec 6000 salariés doit-elle un plan de vigilance ?
    - Jurisprudence sur le devoir de vigilance
    - Mon entreprise de 50M€ de CA doit-elle un commissaire aux comptes ?
    """
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Saisie utilisateur
user_query = st.chat_input("Posez votre question juridique...")

if user_query:
    # Ajout message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Génération réponse
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyse en cours..."):
            start_time = time.time()
            
            try:
                result = route_and_answer(
                    user_query,
                    use_rag=st.session_state.use_rag,
                    use_jurisprudence=st.session_state.use_jurisprudence
                )
                
                answer = result.get("answer", "Désolé, je n'ai pas pu traiter votre demande.")
                response_time = (time.time() - start_time) * 1000
                
                # Mise à jour stats
                st.session_state.stats["queries_count"] += 1
                if st.session_state.stats["queries_count"] > 1:
                    st.session_state.stats["avg_response_time"] = (
                        (st.session_state.stats["avg_response_time"] * 
                         (st.session_state.stats["queries_count"] - 1) + response_time) / 
                        st.session_state.stats["queries_count"]
                    )
                else:
                    st.session_state.stats["avg_response_time"] = response_time
                
                if result.get("is_rag", False):
                    st.session_state.stats["rag_queries"] += 1
                if result.get("is_citation", False):
                    st.session_state.stats["citation_resolutions"] += 1
                
                st.markdown(answer)
                
                # Affichage des sources
                if st.session_state.show_sources and result.get("sources"):
                    with st.expander("📚 Sources juridiques"):
                        for source in result["sources"][:3]:
                            st.markdown(f"**Article {source.get('article_id', 'Inconnu')}**")
                            st.caption(source.get('hierarchy_path', ''))
                            st.divider()
                
                st.caption(f"⏱️ {response_time:.0f}ms")
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                answer = f"Désolé, une erreur s'est produite: {str(e)}"
                st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})