# src/rag/rag_chain.py 

import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from rag.ingest_comlex import ComplianceVectorStore, ArticleIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_DIR = os.environ.get("COMPLIANCE_VECTOR_DB", "./chroma_db")


@dataclass
class RAGResponse:
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    article_ids: List[str]
    retrieval_time_ms: float


class ComplianceRAGChain:
    def __init__(self):
        logger.info("Initialisation de la chaîne RAG")
        self.vstore = ComplianceVectorStore()
        try:
            self.vectorstore = self.vstore.load()
            self.article_indexer = self.vstore.article_indexer
        except Exception as e:
            logger.warning(f"Erreur: {e}")
            self.vectorstore = None
            self.article_indexer = ArticleIndexer()
    
    def answer(self, question: str, k: int = 5) -> RAGResponse:
        import time
        start_time = time.time()
        
        # Vérifier citation directe
        citation = self._extract_citation(question)
        if citation:
            article = self.article_indexer.resolve(citation)
            if article:
                return RAGResponse(
                    answer=f"**Article {citation}**\n\n{article.content}",
                    sources=[{"article_id": citation, "content": article.content[:500]}],
                    confidence=1.0,
                    article_ids=[citation],
                    retrieval_time_ms=(time.time() - start_time) * 1000
                )
        
        # Recherche vectorielle
        if not self.vectorstore:
            return RAGResponse(
                answer="Le système RAG n'est pas initialisé.",
                sources=[], confidence=0.0, article_ids=[],
                retrieval_time_ms=(time.time() - start_time) * 1000
            )
        
        docs = self.vectorstore.similarity_search(question, k=k)
        
        if not docs:
            return RAGResponse(
                answer="Aucun article pertinent trouvé.",
                sources=[], confidence=0.0, article_ids=[],
                retrieval_time_ms=(time.time() - start_time) * 1000
            )
        
        # Construction réponse
        answer_parts = ["Voici les informations trouvées dans le Code de commerce:\n"]
        article_ids = []
        
        for i, doc in enumerate(docs[:3], 1):
            article_id = doc.metadata.get("article_id", "Inconnu")
            content = doc.page_content[:600]
            answer_parts.append(f"**{i}. Article {article_id}**\n{content}\n")
            if article_id != "Inconnu":
                article_ids.append(article_id)
        
        return RAGResponse(
            answer="\n".join(answer_parts),
            sources=[{"article_id": aid} for aid in article_ids],
            confidence=0.8,
            article_ids=article_ids,
            retrieval_time_ms=(time.time() - start_time) * 1000
        )
    
    def _extract_citation(self, text: str) -> Optional[str]:
        pattern = r'(L\.|R\.|D\.|A\.)?\s*(\d{1,3}(?:[-.]\d{1,3}){0,4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            prefix = match.group(1) or "L"
            num = match.group(2)
            return f"{prefix}.{num}"
        return None


_rag_chain = None


def get_rag_chain() -> ComplianceRAGChain:
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = ComplianceRAGChain()
    return _rag_chain