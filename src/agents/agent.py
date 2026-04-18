"""
Agent conversationnel pour l'assistant de conformité commerciale
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """États de l'agent"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"


@dataclass
class ConversationTurn:
    """Tour de conversation"""
    user_query: str
    agent_response: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConversationContext:
    """Contexte de conversation"""
    session_id: str
    history: List[ConversationTurn] = field(default_factory=list)
    last_article: Optional[str] = None


class ComplianceAgent:
    """Agent conversationnel pour la conformité commerciale"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.context = ConversationContext(session_id=session_id)
        self._router = None
        self.state = AgentState.IDLE
        logger.info(f"Agent initialisé - Session: {session_id}")
    
    @property
    def router(self):
        """Lazy loading du routeur"""
        if self._router is None:
            from agents.router import get_router
            self._router = get_router()
        return self._router
    
    def process(self, query: str, use_rag: bool = True, use_jurisprudence: bool = True) -> Dict[str, Any]:
        """Traite une requête utilisateur"""
        start_time = time.time()
        self.state = AgentState.PROCESSING
        
        try:
            result = self.router.route(query, use_rag, use_jurisprudence)
            
            turn = ConversationTurn(user_query=query, agent_response=result.get("answer", ""))
            self.context.history.append(turn)
            
            if result.get("articles"):
                self.context.last_article = result["articles"][0]
            
            result["response_time_ms"] = (time.time() - start_time) * 1000
            self.state = AgentState.COMPLETED
            return result
            
        except Exception as e:
            logger.error(f"Erreur: {e}")
            self.state = AgentState.IDLE
            return {
                "answer": f"Désolé, une erreur s'est produite: {str(e)}",
                "sources": [],
                "articles": [],
                "response_time_ms": (time.time() - start_time) * 1000
            }
    
    def clear_history(self):
        """Efface l'historique"""
        self.context.history = []
        logger.info("Historique effacé")
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques"""
        return {
            "session_id": self.session_id,
            "total_queries": len(self.context.history),
            "state": self.state.value,
            "last_article": self.context.last_article
        }


_agent_instance = None


def get_agent(session_id: str = "default") -> ComplianceAgent:
    """Singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ComplianceAgent(session_id)
    return _agent_instance