"""
Routeur pour l'assistant de conformité commerciale
Oriente les requêtes vers les bons outils et construit les réponses
"""

import time
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from tools import get_tools_instance

try:
    from tools.rag_tool import get_rag_tool
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

try:
    from tools.judilibre_tool import get_judilibre_tool
    JUDILIBRE_AVAILABLE = False  # Désactivé pour éviter les erreurs
except ImportError:
    JUDILIBRE_AVAILABLE = False

try:
    from tools.entrepreneur_tool import get_entrepreneur_tool
    ENTREPRENEUR_AVAILABLE = True
except ImportError:
    ENTREPRENEUR_AVAILABLE = False

try:
    from tools.metier_tool import get_metier_tool
    METIER_AVAILABLE = True
except ImportError:
    METIER_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceRouter:
    """Routeur pour les requêtes de conformité"""
    
    def __init__(self):
        self.tools = get_tools_instance()
        self.rag_tool = get_rag_tool() if RAG_AVAILABLE else None
        self.judilibre = get_judilibre_tool() if JUDILIBRE_AVAILABLE else None
        self.entrepreneur_tool = get_entrepreneur_tool() if ENTREPRENEUR_AVAILABLE else None
        self.metier_tool = get_metier_tool() if METIER_AVAILABLE else None
        logger.info("Routeur initialisé")
    
    def _extract_citation(self, query: str) -> Optional[str]:
        """Extrait une citation d'article"""
        patterns = [
            r'(?:Article\s+)?(L\.|R\.|D\.|A\.)\s*(\d{1,3}(?:[-.]\d{1,3}){0,4})',
            r'art\.?\s*(L\.|R\.|D\.|A\.)\s*(\d{1,3}(?:[-.]\d{1,3}){0,4})',
            r'([L|R|D|A]\.\s*\d{1,3}(?:[-.]\d{1,3}){0,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}.{match.group(2)}"
                elif len(match.groups()) == 1:
                    return match.group(1)
        return None
    
    def _is_metier_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Détecte une question sur un métier spécifique - Version prioritaire"""
        query_lower = query.lower()
        
        # Mapping métier -> mots-clés (ordre de priorité)
        metier_mapping = [
            ("formateur", ["formateur", "professeur", "enseignant", "pédagogie", "former", "formation"]),
            ("consultant", ["consultant", "conseil", "stratégie d'entreprise", "conseiller"]),
            ("commercial", ["commercial", "vente", "business development", "prospection commerciale"]),
            ("marketing", ["marketing digital", "seo", "google ads", "community manager"]),
            ("redacteur", ["rédacteur web", "copywriter", "contenu web", "rédacteur"]),
            ("photographe", ["photographe", "photo", "cliché", "portrait"]),
            ("designer", ["designer", "ui ux", "figma", "graphiste"]),
            ("developpeur", ["développeur", "dev", "programmeur", "python", "javascript"]),
            ("coach_sportif", ["coach sportif", "personal trainer"]),
            ("traducteur", ["traducteur", "interprète"]),
            ("comptable", ["comptable", "expert comptable"]),
            ("electricien", ["électricien", "elec"]),
            ("plombier", ["plombier", "sanitaire"]),
            ("infirmier", ["infirmier", "infirmière"]),
            ("avocat", ["avocat", "juriste"]),
        ]
        
        for metier, keywords in metier_mapping:
            for keyword in keywords:
                if keyword in query_lower:
                    logger.info(f"Métier détecté: {metier} (mot-clé: {keyword})")
                    return True, metier
        
        return False, None
    
    def _is_entrepreneur_query(self, query: str) -> bool:
        """Détecte une requête sur l'entrepreneuriat"""
        query_lower = query.lower()
        entrepreneur_keywords = [
            "auto entrepreneur", "auto-entrepreneur", "micro entrepreneur",
            "devenir auto", "créer son entreprise", "statut juridique"
        ]
        return any(kw in query_lower for kw in entrepreneur_keywords)
    
    def route(self, query: str, use_rag: bool = True, use_jurisprudence: bool = True) -> Dict[str, Any]:
        """Route la requête vers le bon handler"""
        start_time = time.time()
        
        # 1. PRIORITÉ ABSOLUE: Vérifier si c'est une question sur un métier
        is_metier, metier = self._is_metier_query(query)
        if is_metier and metier and self.metier_tool:
            try:
                result = self.metier_tool.answer(query)
                if result and result.confidence > 0.5:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "answer": result.answer,
                        "sources": [{"source": s, "type": "metier"} for s in result.sources],
                        "articles": [],
                        "response_time_ms": response_time,
                        "is_citation": False,
                        "is_rag": False,
                        "is_entrepreneur": False,
                        "is_metier": True,
                        "domain": result.domain,
                        "jurisprudence": []
                    }
            except Exception as e:
                logger.error(f"Erreur metier tool: {e}")
        
        # 2. Vérifier si c'est une citation directe d'article
        citation = self._extract_citation(query)
        if citation:
            article = self.tools.resolve_citation(citation)
            if article:
                response_time = (time.time() - start_time) * 1000
                return {
                    "answer": f"**Article {citation}**\n\n{article.get('content', '')}",
                    "sources": [{"article_id": citation, "content": article.get('content', '')[:500]}],
                    "articles": [citation],
                    "response_time_ms": response_time,
                    "is_citation": True,
                    "is_rag": False,
                    "is_entrepreneur": False,
                    "is_metier": False,
                    "jurisprudence": []
                }
        
        # 3. Vérifier si c'est une requête entrepreneuriat
        if self._is_entrepreneur_query(query) and self.entrepreneur_tool:
            try:
                result = self.entrepreneur_tool.answer(query)
                if result and result.confidence > 0.5:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "answer": result.answer,
                        "sources": [{"source": s, "type": "entrepreneur"} for s in result.sources],
                        "articles": [],
                        "response_time_ms": response_time,
                        "is_citation": False,
                        "is_rag": False,
                        "is_entrepreneur": True,
                        "is_metier": False,
                        "jurisprudence": []
                    }
            except Exception as e:
                logger.error(f"Erreur entrepreneur tool: {e}")
        
        # 4. Recherche RAG (Code de commerce)
        if use_rag and self.rag_tool:
            try:
                rag_result = self.rag_tool.query(query)
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "answer": rag_result.answer,
                    "sources": rag_result.sources,
                    "articles": rag_result.article_ids,
                    "response_time_ms": response_time,
                    "is_rag": True,
                    "is_citation": False,
                    "is_entrepreneur": False,
                    "is_metier": False,
                    "jurisprudence": []
                }
            except Exception as e:
                logger.error(f"Erreur RAG: {e}")
        
        # 5. Fallback
        response_time = (time.time() - start_time) * 1000
        return {
            "answer": "Désolé, je n'ai pas trouvé d'information pertinente. Essayez de reformuler votre question.",
            "sources": [],
            "articles": [],
            "response_time_ms": response_time,
            "is_citation": False,
            "is_rag": False,
            "is_entrepreneur": False,
            "is_metier": False,
            "jurisprudence": []
        }


# Singleton
_router_instance = None


def get_router() -> ComplianceRouter:
    """Récupère l'instance unique du routeur"""
    global _router_instance
    if _router_instance is None:
        _router_instance = ComplianceRouter()
    return _router_instance


def route_and_answer(query: str, use_rag: bool = True, use_jurisprudence: bool = True) -> Dict[str, Any]:
    """Interface simple pour l'application Streamlit"""
    router = get_router()
    return router.route(query, use_rag, use_jurisprudence)