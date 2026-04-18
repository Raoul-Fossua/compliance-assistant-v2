"""
Outils principaux pour l'assistant de conformité commerciale
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
METADATA_DIR = os.environ.get("COMPLIANCE_METADATA_DIR", "./metadata")
Path(METADATA_DIR).mkdir(parents=True, exist_ok=True)


@dataclass
class ThresholdResult:
    """Résultat de vérification de seuil"""
    threshold_type: str
    is_exceeded: bool
    current_value: float
    required_value: float
    unit: str
    obligation: str
    article_ref: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_message(self) -> str:
        if self.is_exceeded:
            return f"⚠️ **Seuil dépassé** - {self.obligation} (Article {self.article_ref})"
        return f"✅ **Seuil non atteint** - Pas d'obligation (Article {self.article_ref})"


# Seuils du Code de commerce
THRESHOLDS = {
    "devoir_vigilance": {
        "required": {"effectif": 5000, "ca": 150_000_000},
        "unit": "salariés / euros",
        "obligation": "Établir un plan de vigilance",
        "article": "L.225-102-4"
    },
    "commissaire_aux_comptes": {
        "required": {"effectif": 50, "ca": 8_000_000},
        "unit": "salariés / euros",
        "obligation": "Nommer un commissaire aux comptes",
        "article": "L.227-9-1"
    },
    "comptes_consolides": {
        "required": {"effectif": 500, "ca": 150_000_000},
        "unit": "salariés / euros",
        "obligation": "Établir des comptes consolidés",
        "article": "L.233-16"
    }
}


# Articles statiques
STATIC_ARTICLES = {
    "L.225-102-4": {
        "id": "L.225-102-4",
        "content": """I. - Les sociétés qui emploient au moins 5000 salariés en France 
ou 10000 salariés dans le monde établissent un plan de vigilance.

II. - Le plan comporte les mesures de vigilance raisonnable pour identifier 
les risques et prévenir les atteintes aux droits humains.""",
        "hierarchy_path": "LIVRE II > TITRE II > Chapitre V > Section 2"
    },
    "L.227-9-1": {
        "id": "L.227-9-1",
        "content": """La nomination d'un commissaire aux comptes est obligatoire 
lorsque la société dépasse les seuils de 8M€ de CA ou 50 salariés.""",
        "hierarchy_path": "LIVRE II > TITRE II > Chapitre VII"
    },
    "L.233-16": {
        "id": "L.233-16",
        "content": """Les sociétés qui contrôlent une ou plusieurs entreprises 
sont tenues d'établir des comptes consolidés.""",
        "hierarchy_path": "LIVRE II > TITRE III > Chapitre III"
    }
}


class ComplianceTools:
    """Outils de conformité"""
    
    def __init__(self):
        self.articles = STATIC_ARTICLES.copy()
        logger.info(f"Tools initialisés: {len(self.articles)} articles")
    
    def resolve_citation(self, article_id: str) -> Optional[Dict]:
        """Résout une citation d'article"""
        article_id = article_id.upper()
        if article_id in self.articles:
            return self.articles[article_id]
        return None
    
    def compute_threshold(self, threshold_type: str, ca: float = None, effectif: int = None) -> Optional[ThresholdResult]:
        """Vérifie les seuils"""
        if threshold_type not in THRESHOLDS:
            return None
        
        config = THRESHOLDS[threshold_type]
        required = config["required"]
        is_exceeded = False
        current = 0
        required_val = 0
        
        if ca and required.get("ca"):
            if ca >= required["ca"]:
                is_exceeded = True
                current = ca
                required_val = required["ca"]
        
        if effectif and required.get("effectif"):
            if effectif >= required["effectif"]:
                is_exceeded = True
                current = effectif
                required_val = required["effectif"]
        
        return ThresholdResult(
            threshold_type=threshold_type,
            is_exceeded=is_exceeded,
            current_value=current,
            required_value=required_val,
            unit=config["unit"],
            obligation=config["obligation"],
            article_ref=config["article"]
        )
    
    def search_code(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recherche dans le Code"""
        results = []
        query_lower = query.lower()
        
        for aid, article in self.articles.items():
            if query_lower in article["content"].lower():
                results.append({
                    "article_id": aid,
                    "content": article["content"][:500],
                    "relevance_score": 0.8
                })
        
        return results[:top_k]
    
    def get_article_context(self, article_id: str, depth: int = 1) -> Dict:
        """Récupère un article avec son contexte"""
        article = self.resolve_citation(article_id)
        if not article:
            return {"error": f"Article {article_id} non trouvé"}
        return article


_compliance_tools = None


def get_tools_instance() -> ComplianceTools:
    """Singleton"""
    global _compliance_tools
    if _compliance_tools is None:
        _compliance_tools = ComplianceTools()
    return _compliance_tools


def resolve_citation(article_id: str) -> Optional[Dict]:
    return get_tools_instance().resolve_citation(article_id)


def compute_threshold(threshold_type: str, ca: float = None, effectif: int = None) -> Optional[ThresholdResult]:
    return get_tools_instance().compute_threshold(threshold_type, ca, effectif)


def search_code(query: str, top_k: int = 5) -> List[Dict]:
    return get_tools_instance().search_code(query, top_k)


def get_article_context(article_id: str, depth: int = 1) -> Dict:
    return get_tools_instance().get_article_context(article_id, depth)

def validate_compliance(company_data: Dict[str, Any], query: str = "") -> Dict[str, Any]:
    """
    Valide la conformité d'une entreprise
    
    Args:
        company_data: Données de l'entreprise (nom, CA, effectif, forme juridique)
        query: Requête optionnelle
        
    Returns:
        Rapport de conformité
    """
    tools = get_tools_instance()
    
    results = {
        "company": company_data.get("nom", "Entreprise"),
        "checked_at": datetime.now().isoformat(),
        "obligations": [],
        "alerts": [],
        "recommendations": []
    }
    
    # Vérifier le devoir de vigilance
    if company_data.get("effectif", 0) >= 5000 or company_data.get("ca", 0) >= 150_000_000:
        result = tools.compute_threshold("devoir_vigilance", 
                                          ca=company_data.get("ca"),
                                          effectif=company_data.get("effectif"))
        if result:
            results["obligations"].append({
                "type": "devoir_vigilance",
                "obligation": result.obligation,
                "article": result.article_ref
            })
            results["recommendations"].append(
                "Établir et publier un plan de vigilance conforme à l'article L. 225-102-4"
            )
    
    # Vérifier le commissaire aux comptes
    forme = company_data.get("forme_juridique", "").lower()
    if any(f in forme for f in ["sas", "sarl", "sa"]):
        if company_data.get("effectif", 0) >= 50 or company_data.get("ca", 0) >= 8_000_000:
            result = tools.compute_threshold("commissaire_aux_comptes",
                                              ca=company_data.get("ca"),
                                              effectif=company_data.get("effectif"))
            if result:
                results["obligations"].append({
                    "type": "commissaire_aux_comptes",
                    "obligation": result.obligation,
                    "article": result.article_ref
                })
    
    results["status"] = "alerte" if results["obligations"] else "conforme"
    
    return results
