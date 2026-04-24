"""
Routeur avec vrai RAG vectoriel pour le Code de commerce
"""

import time
import re
import logging
from typing import Dict, Any

from tools.comprehensive_tool import get_comprehensive_tool

try:
    from rag.ingest_comlex import get_vectorstore
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGRouter:
    def __init__(self):
        self.metier_tool = get_comprehensive_tool()
        self.vectorstore = None
        
        if RAG_AVAILABLE:
            try:
                self.vectorstore = get_vectorstore()
                if self.vectorstore:
                    logger.info("✅ RAG vectoriel chargé - 2100 pages du Code de commerce")
                else:
                    logger.warning("⚠️ Vectorstore non disponible")
            except Exception as e:
                logger.warning(f"Erreur: {e}")
    
    def _is_metier_question(self, query: str) -> bool:
        """Détecte les questions métiers"""
        q = query.lower()
        metiers = ["plombier", "menuisier", "electricien", "formateur", 
                   "photographe", "consultant", "commercial", "développeur",
                   "coiffeur", "infirmier", "avocat", "architecte"]
        indicators = ["comment devenir", "conseils pour devenir", "métier", "freelance", "auto emploi"]
        return any(m in q for m in metiers) or any(i in q for i in indicators)
    
    def route(self, query: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Questions métiers → ComprehensiveTool
        if self._is_metier_question(query):
            logger.info("→ Route: Métier")
            result = self.metier_tool.answer(query)
            return {
                "answer": result.answer,
                "category": "metier",
                "source": "comprehensive_tool",
                "response_time_ms": (time.time() - start_time) * 1000
            }
        
        # 2. RAG vectoriel pour le Code de commerce
        if self.vectorstore:
            try:
                logger.info("→ Route: RAG Vectoriel sur 2100 pages")
                docs = self.vectorstore.similarity_search(query, k=4)
                
                if docs:
                    # Construire la réponse avec les sources
                    answer = f"""## 📖 Réponse basée sur le Code de commerce (recherche vectorielle)

**Votre question :** {query}

**Extraits pertinents trouvés :**

"""
                    for i, doc in enumerate(docs, 1):
                        # Nettoyer le contenu
                        content = doc.page_content[:600]
                        article_id = doc.metadata.get('article_id', 'Article inconnu')
                        livre = doc.metadata.get('livre', '')
                        chapitre = doc.metadata.get('chapitre', '')
                        
                        answer += f"""
### 📌 Extrait {i} - Article {article_id}
*{livre} > {chapitre}*

{content}...

---
"""
                    
                    answer += """
⚠️ **Information** : Cette réponse est générée par recherche automatique dans le Code de commerce. Pour un avis juridique définitif, consultez un professionnel.
"""
                    return {
                        "answer": answer,
                        "category": "code",
                        "source": "rag_vectoriel",
                        "documents": len(docs),
                        "response_time_ms": (time.time() - start_time) * 1000
                    }
            except Exception as e:
                logger.error(f"Erreur RAG: {e}")
        
        # 3. Fallback
        result = self.metier_tool.answer(query)
        return {
            "answer": result.answer,
            "category": "general",
            "source": "fallback",
            "response_time_ms": (time.time() - start_time) * 1000
        }


_router = None


def get_router():
    global _router
    if _router is None:
        _router = RAGRouter()
    return _router


def route_and_answer(query: str, **kwargs) -> Dict[str, Any]:
    return get_router().route(query)
