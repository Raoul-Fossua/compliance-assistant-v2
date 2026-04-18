"""
Tools pour l'assistant de conformité commerciale
Exporte tous les outils disponibles pour l'agent et le routeur
"""

from .tools import (
    get_tools_instance,
    ComplianceTools,
    ThresholdResult,
    search_code,
    resolve_citation,
    compute_threshold,
    get_article_context
)

from .rag_tool import (
    get_rag_tool,
    RAGTool,
    RAGResult,
    rag_search,
    rag_get_article,
    rag_search_articles
)

from .judilibre_tool import (
    get_judilibre_tool,
    JudilibreTool,
    JurisprudenceDecision,
    search_jurisprudence,
    search_jurisprudence_text
)

from .entrepreneur_tool import (
    get_entrepreneur_tool,
    EntrepreneurTool,
    EntrepreneurResponse
)

from .metier_tool import (
    get_metier_tool,
    MetierTool,
    MetierResponse
)

__all__ = [
    # Tools principaux
    "get_tools_instance",
    "ComplianceTools",
    "ThresholdResult",
    "search_code",
    "resolve_citation",
    "compute_threshold",
    "get_article_context",
    
    # RAG Tool
    "get_rag_tool",
    "RAGTool",
    "RAGResult",
    "rag_search",
    "rag_get_article",
    "rag_search_articles",
    
    # Judilibre Tool
    "get_judilibre_tool",
    "JudilibreTool",
    "JurisprudenceDecision",
    "search_jurisprudence",
    "search_jurisprudence_text",
    
    # Entrepreneur Tool
    "get_entrepreneur_tool",
    "EntrepreneurTool",
    "EntrepreneurResponse",
    
    # Métier Tool
    "get_metier_tool",
    "MetierTool",
    "MetierResponse"
]