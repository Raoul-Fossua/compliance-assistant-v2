"""
Routeur pour l'assistant de conformité commerciale
Version simplifiée utilisant ComprehensiveTool
"""

import time
import re
import logging
from typing import Dict, Any, Optional

from tools.comprehensive_tool import get_comprehensive_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceRouter:
    def __init__(self):
        self.tool = get_comprehensive_tool()
        logger.info("Routeur initialisé avec ComprehensiveTool")
    
    def route(self, query: str, use_rag: bool = True, use_jurisprudence: bool = True) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            result = self.tool.answer(query)
            response_time = (time.time() - start_time) * 1000
            
            return {
                "answer": result.answer,
                "sources": [],
                "articles": [],
                "response_time_ms": response_time,
                "category": result.category,
                "confidence": result.confidence
            }
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return {
                "answer": "Désolé, une erreur s'est produite. Veuillez réessayer.",
                "sources": [],
                "articles": [],
                "response_time_ms": (time.time() - start_time) * 1000,
                "category": "error"
            }


_router_instance = None


def get_router() -> ComplianceRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ComplianceRouter()
    return _router_instance


def route_and_answer(query: str, use_rag: bool = True, use_jurisprudence: bool = True) -> Dict[str, Any]:
    router = get_router()
    return router.route(query, use_rag, use_jurisprudence)
