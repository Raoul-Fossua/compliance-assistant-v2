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
# CONFIGURATION DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="Assistant de Conformité Commerciale",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLES CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb4d);
        background-size: 200% 200%;
        animation: gradient 15s ease infinite;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .card h3 {
        margin-top: 0;
        color: #1a2a6c;
    }
    .objectif-card {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
    }
    .objectif-icon {
        font-size: 2rem;
        margin-right: 1rem;
        vertical-align: middle;
    }
    .badge {
        display: inline-block;
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        color: #666;
        font-size: 0.8rem;
        border-top: 1px solid #ddd;
    }
    .statut {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .statut-fonctionnel {
        background-color: #4caf50;
        color: white;
    }
    .statut-partiel {
        background-color: #ff9800;
        color: white;
    }
    .statut-a-venir {
        background-color: #9e9e9e;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALISATION DE SESSION STATE
# ============================================================================

def init_session_state():
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
# EN-TÊTE AVEC OBJECTIFS
# ============================================================================

def display_header():
    """Affiche l'en-tête avec les objectifs de l'assistant"""
    
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Assistant de Conformité Commerciale</h1>
        <p>Recherche intelligente dans le Code de commerce | Jurisprudence | Vérification de seuils | Orientation professionnelle</p>
    </div>
    """, unsafe_allow_html=True)
    
    # === OBJECTIFS DE L'ASSISTANT ===
    st.markdown("## 🎯 Notre mission : vos droits et votre avenir professionnel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card objectif-card">
            <h3>📖 1. Comprendre le droit</h3>
            <p><strong>🎯 Objectif :</strong> Rendre le <strong>Code de commerce</strong> accessible à tous</p>
            <p>✅ Consultation des articles par citation directe</p>
            <p>✅ Recherche sémantique dans 2100 pages de textes</p>
            <p>✅ Réponses en langage clair, pas de jargon juridique</p>
            <p>🔜 Vérification automatique des obligations légales</p>
            <span class="statut statut-fonctionnel">✅ Fonctionnel</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card objectif-card">
            <h3>🚀 2. Guider les jeunes diplômés</h3>
            <p><strong>🎯 Objectif :</strong> Aider à <strong>se lancer dans la vie active</strong></p>
            <p>✅ Conseils par métier (développeur, plombier, formateur...)</p>
            <p>✅ Choix du statut juridique (auto-entrepreneur, EURL, SASU)</p>
            <p>✅ Formations recommandées et salaires estimés</p>
            <p>✅ Aides financières disponibles (ACRE, NACRE...)</p>
            <span class="statut statut-fonctionnel">✅ Fonctionnel</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card objectif-card">
            <h3>💼 3. Orienter vers les métiers</h3>
            <p><strong>🎯 Objectif :</strong> Proposer un <strong>guide sur mesure</strong> pour chaque métier</p>
            <p>✅ Formations nécessaires</p>
            <p>✅ Tarifs et revenus attendus</p>
            <p>✅ Étapes concrètes pour se lancer</p>
            <p>✅ Plateformes pour trouver des missions</p>
            <span class="statut statut-fonctionnel">✅ Fonctionnel</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Deuxième ligne d'objectifs
    st.markdown("---")
    st.markdown("## 📊 État d'avancement des fonctionnalités")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h4>🔍 Recherche d'articles</h4>
            <p>Consultation par citation directe</p>
            <span class="statut statut-fonctionnel">✅ Fonctionnel</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h4>📊 Vérification de seuils</h4>
            <p>CA, effectif, obligations légales</p>
            <span class="statut statut-fonctionnel">✅ Fonctionnel</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h4>💼 Guides métiers</h4>
            <p>10+ métiers disponibles</p>
            <span class="statut statut-fonctionnel">✅ Fonctionnel</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="card">
            <h4>⚖️ Jurisprudence</h4>
            <p>Décisions de justice</p>
            <span class="statut statut-partiel">🔄 En développement</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

def display_welcome_message():
    """Affiche le message d'accueil avec les exemples"""
    
    welcome = """
## 👋 Bonjour ! Je suis votre assistant de conformité commerciale

### 💬 Voici ce que je peux faire pour vous :

| Type | Exemples de questions |
|:---|:---|
| **📖 Code de commerce** | `"Que dit l'article L.225-102-4 ?"` |
| **⚖️ Obligations légales** | `"Une entreprise avec 6000 salariés doit-elle un plan de vigilance ?"` |
| **💼 Conseils métiers** | `"Comment devenir menuisier à son compte ?"` |
| **🎓 Jeunes diplômés** | `"Quel statut choisir pour débuter en freelance ?"` |
| **💰 Aides financières** | `"Quelles aides pour un jeune créateur d'entreprise ?"` |
| **📝 Démarches** | `"Quelles sont les étapes pour créer son entreprise ?"` |

### 🎯 Objectifs de l'assistant

1. **Rendre le droit accessible** : Comprendre vos obligations sans avocat
2. **Guider les jeunes diplômés** : Se lancer avec les bonnes informations
3. **Orienter vers les métiers** : Formation, statut, revenus, étapes

💡 **Posez votre question en langage naturel, je m'occupe du reste !**
    """
    
    return welcome

# ============================================================================
# SIDEBAR
# ============================================================================

def display_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/justice.png", width=80)
        st.title("⚖️ Conformité Commerciale")
        st.caption("Assistant basé sur le Code de commerce")
        st.divider()
        
        st.subheader("⚙️ Configuration")
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
        
        st.subheader("📚 Métiers disponibles")
        st.markdown("""
        - Développeur
        - Plombier
        - Électricien
        - Menuisier
        - Formateur
        - Consultant
        - Commercial
        - Photographe
        - Et plus...
        """)
        
        st.divider()
        
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ============================================================================
# CORPS PRINCIPAL
# ============================================================================

init_session_state()

# Affichage de l'en-tête avec objectifs
display_header()

# Sidebar
display_sidebar()

# Titre principal
st.title("💬 Assistant Conversationnel")

# Message d'accueil
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": display_welcome_message()})

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Saisie utilisateur
user_query = st.chat_input("Posez votre question...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
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
                
                st.session_state.stats["queries_count"] += 1
                if st.session_state.stats["queries_count"] > 1:
                    st.session_state.stats["avg_response_time"] = (
                        (st.session_state.stats["avg_response_time"] * 
                         (st.session_state.stats["queries_count"] - 1) + response_time) / 
                        st.session_state.stats["queries_count"]
                    )
                else:
                    st.session_state.stats["avg_response_time"] = response_time
                
                st.markdown(answer)
                
                if st.session_state.show_sources and result.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in result["sources"][:3]:
                            st.markdown(f"- {source.get('article_id', 'Source')}")
                
                st.caption(f"⏱️ {response_time:.0f}ms")
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                st.markdown("Désolé, une erreur s'est produite. Veuillez réessayer.")
    
    st.session_state.messages.append({"role": "assistant", "content": answer})

# Footer
st.markdown("""
<div class="footer">
    <p>⚖️ Assistant de Conformité Commerciale v2.0 | Basé sur le Code de commerce français | 
    <a href="https://huggingface.co/spaces/Raoul-Fossua/compliance-assistant" target="_blank">🌐 Accès en ligne</a></p>
    <p style="font-size: 0.7rem;">⚠️ Cet assistant fournit des informations générales. Pour un avis juridique personnalisé, consultez un professionnel.</p>
</div>
""", unsafe_allow_html=True)