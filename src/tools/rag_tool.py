"""
RAG Tool pour l'assistant de conformité commerciale
"""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from tools import get_tools_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """Résultat d'une requête RAG"""
    query: str
    answer: str
    sources: List[Dict]
    article_ids: List[str]
    confidence: float = 0.8
    retrieval_time_ms: float = 0
    is_citation_direct: bool = False


class RAGTool:
    """Outil de recherche RAG"""
    
    def __init__(self):
        self.tools = get_tools_instance()
        logger.info("RAG Tool initialisé")
    
    def query(self, query: str, k: int = 5) -> RAGResult:
        """Exécute une requête RAG"""
        start_time = time.time()
        
        # Recherche dans le Code
        results = self.tools.search_code(query, top_k=k)
        
        if not results:
            return RAGResult(
                query=query,
                answer="Aucun article pertinent trouvé dans le Code de commerce.",
                sources=[],
                article_ids=[],
                retrieval_time_ms=(time.time() - start_time) * 1000
            )
        
        # Construction de la réponse
        answer_parts = ["Voici les informations trouvées dans le Code de commerce:\n"]
        article_ids = []
        
        for i, r in enumerate(results[:3], 1):
            article_id = r.get("article_id")
            content = r.get("content", "")
            answer_parts.append(f"**{i}. Article {article_id}**\n{content}\n")
            if article_id:
                article_ids.append(article_id)
        
        answer = "\n".join(answer_parts)
        
        return RAGResult(
            query=query,
            answer=answer,
            sources=results[:3],
            article_ids=article_ids,
            retrieval_time_ms=(time.time() - start_time) * 1000
        )
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Récupère un article"""
        return self.tools.resolve_citation(article_id)
    
    def search_articles(self, query: str, k: int = 5) -> List[Dict]:
        """Recherche des articles sans génération LLM"""
        return self.tools.search_code(query, top_k=k)


# Singleton
_rag_tool = None


def get_rag_tool() -> RAGTool:
    """Singleton"""
    global _rag_tool
    if _rag_tool is None:
        _rag_tool = RAGTool()
    return _rag_tool


# Wrappers pour l'agent (interfaces standardisées)
def rag_search(query: str, k: int = 5) -> Dict[str, Any]:
    """
    Recherche RAG - Interface standardisée pour l'agent
    
    Args:
        query: Question ou requête
        k: Nombre de documents à considérer
        
    Returns:
        Dictionnaire avec la réponse et les sources
    """
    tool = get_rag_tool()
    result = tool.query(query, k)
    return {
        "query": result.query,
        "answer": result.answer,
        "sources": result.sources,
        "article_ids": result.article_ids,
        "confidence": result.confidence,
        "retrieval_time_ms": result.retrieval_time_ms
    }


def rag_get_article(article_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère un article spécifique
    
    Args:
        article_id: ID de l'article (ex: L.225-102-4)
        
    Returns:
        Article complet ou None
    """
    tool = get_rag_tool()
    return tool.get_article(article_id)


def rag_search_articles(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Recherche des articles sans génération LLM
    
    Args:
        query: Requête de recherche
        k: Nombre de résultats
        
    Returns:
        Liste d'articles
    """
    tool = get_rag_tool()
    return tool.search_articles(query, k)