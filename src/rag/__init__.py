"""
Package RAG pour l'ingestion du Code de commerce
"""

from .ingest_comlex import (
    build_vectorstore,
    ComplianceVectorStore,
    HierarchicalCodeSplitter,
    ArticleIndexer
)

__all__ = [
    "build_vectorstore",
    "ComplianceVectorStore",
    "HierarchicalCodeSplitter",
    "ArticleIndexer"
]