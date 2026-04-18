"""
Judilibre Tool - Recherche jurisprudentielle
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = os.environ.get("COMPLIANCE_CACHE_DIR", "./cache/judilibre")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)


@dataclass
class JurisprudenceDecision:
    """Décision de justice"""
    id: str
    title: str
    date: str
    jurisdiction: str
    summary: str
    url: str
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "jurisdiction": self.jurisdiction,
            "summary": self.summary,
            "url": self.url
        }


class JudilibreTool:
    """Tool pour la jurisprudence"""
    
    def __init__(self):
        self.cache_dir = Path(CACHE_DIR)
        self.enabled = False  # Mode démo par défaut
        logger.info("JudilibreTool initialisé (mode démo)")
    
    def _get_cache_key(self, article_id: str) -> str:
        return hashlib.sha256(f"jurisprudence_{article_id}".encode()).hexdigest()
    
    def _get_cached(self, article_id: str) -> Optional[List[Dict]]:
        cache_file = self.cache_dir / f"{self._get_cache_key(article_id)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
                if datetime.now() - cached_at < timedelta(days=7):
                    return data.get("decisions", [])
            except Exception:
                pass
        return None
    
    def _set_cache(self, article_id: str, decisions: List[Dict]):
        cache_file = self.cache_dir / f"{self._get_cache_key(article_id)}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "decisions": decisions,
                    "_cached_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Erreur cache: {e}")
    
    def _get_mock_decisions(self, article_id: str) -> List[JurisprudenceDecision]:
        """Données mockées"""
        mock = {
            "L.225-102-4": [
                JurisprudenceDecision(
                    id="1",
                    title="Cass. com., 15 mars 2023, n° 21-18.456",
                    date="2023-03-15",
                    jurisdiction="Cour de cassation",
                    summary="La Cour rappelle que le devoir de vigilance s'applique aux sociétés mères.",
                    url="https://www.legifrance.gouv.fr"
                ),
                JurisprudenceDecision(
                    id="2",
                    title="CA Paris, 12 janv. 2024, n° 22/04567",
                    date="2024-01-12",
                    jurisdiction="Cour d'appel",
                    summary="Extension du devoir de vigilance aux sous-traitants indirects.",
                    url="https://www.legifrance.gouv.fr"
                )
            ],
            "devoir de vigilance": [
                JurisprudenceDecision(
                    id="3",
                    title="Cass. com., 15 mars 2023, n° 21-18.456",
                    date="2023-03-15",
                    jurisdiction="Cour de cassation",
                    summary="La Cour rappelle que le devoir de vigilance s'applique aux sociétés mères.",
                    url="https://www.legifrance.gouv.fr"
                )
            ]
        }
        return mock.get(article_id, [])
    
    def search_by_article(self, article_id: str, max_results: int = 5) -> List[JurisprudenceDecision]:
        """Recherche la jurisprudence pour un article"""
        cached = self._get_cached(article_id)
        if cached:
            return [JurisprudenceDecision(**d) for d in cached[:max_results]]
        
        decisions = self._get_mock_decisions(article_id)
        self._set_cache(article_id, [d.to_dict() for d in decisions])
        return decisions[:max_results]
    
    def search_by_text(self, query: str, max_results: int = 5) -> List[JurisprudenceDecision]:
        """Recherche la jurisprudence par texte libre"""
        cached = self._get_cached(query)
        if cached:
            return [JurisprudenceDecision(**d) for d in cached[:max_results]]
        
        decisions = self._get_mock_decisions(query)
        self._set_cache(query, [d.to_dict() for d in decisions])
        return decisions[:max_results]


# Singleton
_judilibre_tool = None


def get_judilibre_tool() -> JudilibreTool:
    """Singleton"""
    global _judilibre_tool
    if _judilibre_tool is None:
        _judilibre_tool = JudilibreTool()
    return _judilibre_tool


# Wrappers pour l'agent
def search_jurisprudence(article_id: str, max_results: int = 5) -> List[Dict]:
    """
    Recherche la jurisprudence pour un article
    
    Args:
        article_id: ID de l'article (ex: L.225-102-4)
        max_results: Nombre maximum de résultats
        
    Returns:
        Liste des décisions
    """
    tool = get_judilibre_tool()
    results = tool.search_by_article(article_id, max_results)
    return [r.to_dict() for r in results]


def search_jurisprudence_text(query: str, max_results: int = 5) -> List[Dict]:
    """
    Recherche jurisprudentielle par texte libre
    
    Args:
        query: Texte de recherche
        max_results: Nombre maximum de résultats
        
    Returns:
        Liste des décisions
    """
    tool = get_judilibre_tool()
    results = tool.search_by_text(query, max_results)
    return [r.to_dict() for r in results]