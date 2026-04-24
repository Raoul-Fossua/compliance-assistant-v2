"""
Tools pour l'assistant de conformité commerciale
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

# Importer le nouvel outil complet s'il existe
try:
    from .comprehensive_tool import get_comprehensive_tool, ComprehensiveTool
    COMPREHENSIVE_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_AVAILABLE = False
    print("Comprehensive tool not available")

from .rag_tool import (
    get_rag_tool,
    RAGTool,
    RAGResult
)

from .judilibre_tool import (
    get_judilibre_tool,
    JudilibreTool,
    JurisprudenceDecision
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
    "get_tools_instance",
    "ComplianceTools",
    "ThresholdResult",
    "search_code",
    "resolve_citation",
    "compute_threshold",
    "get_article_context",
    "get_rag_tool",
    "RAGTool",
    "RAGResult",
    "get_judilibre_tool",
    "JudilibreTool",
    "JurisprudenceDecision",
    "get_entrepreneur_tool",
    "EntrepreneurTool",
    "EntrepreneurResponse",
    "get_metier_tool",
    "MetierTool",
    "MetierResponse",
    "get_comprehensive_tool",
    "ComprehensiveTool"
]
