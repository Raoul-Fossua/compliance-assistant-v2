"""
Entrepreneur Tool - Guide pour auto-entrepreneurs et marketing digital
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.environ.get("COMPLIANCE_KNOWLEDGE_DIR", "./knowledge")
KNOWLEDGE_FILE = Path(KNOWLEDGE_DIR) / "entrepreneuriat.json"


@dataclass
class EntrepreneurResponse:
    """Réponse structurée pour les questions entrepreneuriat"""
    answer: str
    sources: List[str]
    confidence: float


class EntrepreneurTool:
    """Tool pour l'accompagnement des auto-entrepreneurs"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge()
        logger.info("EntrepreneurTool initialisé")
    
    def _load_knowledge(self) -> Dict:
        """Charge la base de connaissances"""
        if KNOWLEDGE_FILE.exists():
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Fichier de connaissances non trouvé: {KNOWLEDGE_FILE}")
            return self._get_fallback_knowledge()
    
    def _get_fallback_knowledge(self) -> Dict:
        """Connaissances de secours"""
        return {
            "auto_entrepreneur": {
                "conditions": {"age": "18 ans", "plafond_services": 77700},
                "formalites": {"etapes": ["Déclaration sur guichet unique", "Obtention SIRET"]},
                "cotisations_sociales": {"prestations_services": 21.2}
            }
        }
    
    def detect_intent(self, query: str) -> Optional[str]:
        """Détecte l'intention de la question"""
        query_lower = query.lower()
        
        intents = {
            "auto_entrepreneur_statut": ["auto entrepreneur", "auto-entrepreneur", "micro entrepreneur", "micro-entrepreneur", "statut"],
            "auto_entrepreneur_plafond": ["plafond", "seuil", "chiffre d'affaires", "ca max", "77", "77700"],
            "auto_entrepreneur_etapes": ["comment devenir", "étapes", "formalités", "démarches", "procedure", "procedure"],
            "auto_entrepreneur_cotisations": ["cotisation", "charge", "urssaf", "pourcentage", "taux"],
            "marketing_digital_activites": ["marketing digital", "réseaux sociaux", "seo", "google ads", "community manager"],
            "jeune_diplome_guide": ["jeune diplomé", "jeune diplômé", "sortie d'étude", "premier emploi", "débuter", "guide", "demarche simple"],
            "aides_financieres": ["aide", "subvention", "acre", "nacre", "financement", "prêt"]
        }
        
        for intent, keywords in intents.items():
            if any(kw in query_lower for kw in keywords):
                return intent
        
        return None
    
    def answer(self, query: str) -> EntrepreneurResponse:
        """Répond à une question sur l'entrepreneuriat"""
        
        intent = self.detect_intent(query)
        
        if intent == "jeune_diplome_guide":
            return self._guide_jeune_diplome()
        elif intent == "auto_entrepreneur_etapes":
            return self._guide_etapes()
        elif intent == "auto_entrepreneur_plafond":
            return self._info_plafonds()
        elif intent == "auto_entrepreneur_cotisations":
            return self._info_cotisations()
        elif intent == "marketing_digital_activites":
            return self._info_marketing_digital()
        elif intent == "aides_financieres":
            return self._info_aides()
        else:
            return self._guide_general()
    
    def _guide_jeune_diplome(self) -> EntrepreneurResponse:
        """Guide spécifique pour jeune diplômé en marketing"""
        data = self.knowledge.get("demarche_simple", {}).get("jeune_diplome_marketing", {})
        
        answer = f"""
## 🎓 {data.get('titre', 'Guide pour jeune diplômé')}

### 📋 Étapes clés

"""
        for etape in data.get("etapes", []):
            answer += f"\n**{etape.get('numero')}. {etape.get('titre')}**\n"
            for action in etape.get("actions", []):
                answer += f"   {action}\n"
        
        answer += f"""
### 💰 Aides financières disponibles
"""
        for aide in data.get("aides_financieres", []):
            answer += f"- {aide}\n"
        
        answer += f"""
### 📚 Ressources gratuites
"""
        for res in data.get("ressources_gratuites", []):
            answer += f"- {res}\n"
        
        answer += """
### 💡 Conseil pratique
Commencez par une activité en parallèle de votre emploi (portage salarial ou freelance)
pour tester le marché avant de vous lancer à 100%.
"""
        
        return EntrepreneurResponse(
            answer=answer,
            sources=["urssaf.fr", "bpifrance-creation.fr", "auto-entrepreneur.urssaf.fr"],
            confidence=0.95
        )
    
    def _guide_etapes(self) -> EntrepreneurResponse:
        """Guide des étapes pour devenir auto-entrepreneur"""
        data = self.knowledge.get("auto_entrepreneur", {})
        formalites = data.get("formalites", {})
        
        answer = """
## 📝 Devenir auto-entrepreneur en 5 étapes

### Étape 1 : Vérifier son éligibilité
- ✅ Avoir 18 ans ou plus
- ✅ Ne pas dépasser les plafonds de CA

### Étape 2 : Choisir son activité
- Prestations de services (marketing, consulting)
- Activités commerciales
- Activités libérales

### Étape 3 : Déclarer son début d'activité
- 🌐 Rendez-vous sur le guichet unique : https://formalites.entreprises.gouv.fr
- 📝 Sélectionnez "micro-entrepreneur"
- 📄 Obtenez votre numéro SIRET sous 15 jours

### Étape 4 : Démarrer votre activité
- 📧 Créez une adresse email professionnelle
- 💼 Ouvrez un compte bancaire dédié
- 📋 Rédigez vos CGV et devis

### Étape 5 : Gérer votre administration
- 📅 Déclarez votre CA chaque mois ou trimestre
- 💰 Payez vos cotisations (21.2% pour les services)
- 🧾 Facturez vos clients

## 🔗 Liens utiles
- [Guichet unique](https://formalites.entreprises.gouv.fr)
- [Auto-entrepreneur Urssaf](https://auto-entrepreneur.urssaf.fr)
"""
        return EntrepreneurResponse(
            answer=answer,
            sources=["urssaf.fr", "service-public.fr"],
            confidence=0.9
        )
    
    def _info_plafonds(self) -> EntrepreneurResponse:
        """Informations sur les plafonds"""
        answer = """
## 📊 Plafonds auto-entrepreneur 2026

| Type d'activité | Plafond annuel HT |
|:---|:---:|
| Prestations de services (marketing, consulting) | **77 700 €** |
| Activités commerciales | **188 700 €** |
| Activités libérales réglementées | **77 700 €** |

### ⚠️ Attention
- Dépassement **2 années consécutives** = sortie du régime
- Possibilité de rester si dépassement < 10% une année

### 💡 Conseil
Pour CA > 77 700€, envisagez :
- EURL (entreprise unipersonnelle à responsabilité limitée)
- SASU (société par actions simplifiée unipersonnelle)
"""
        return EntrepreneurResponse(
            answer=answer,
            sources=["legifrance.gouv.fr", "urssaf.fr"],
            confidence=0.95
        )
    
    def _info_cotisations(self) -> EntrepreneurResponse:
        """Informations sur les cotisations"""
        answer = """
## 💶 Cotisations sociales auto-entrepreneur 2026

### Taux applicables
| Activité | Taux | Exemple (CA 1000€) |
|:---|:---:|:---:|
| Prestations de services | **21.2%** | 212€ |
| Activités commerciales | **12.3%** | 123€ |
| Activités libérales | **21.2%** | 212€ |

### Exonération 1ère année (ACRE)
- ✅ **50% de réduction** sur les cotisations
- ✅ Sous conditions de ressources ou statut (jeune diplômé, demandeur d'emploi)

### Ce que couvrent les cotisations
- 🏥 Assurance maladie (remboursement des soins)
- 👵 Retraite de base
- 👨‍👩‍👧 Allocation familiale

### 💡 Conseil
Déclarez chaque mois pour lisser vos paiements !
"""
        return EntrepreneurResponse(
            answer=answer,
            sources=["urssaf.fr", "service-public.fr"],
            confidence=0.95
        )
    
    def _info_marketing_digital(self) -> EntrepreneurResponse:
        """Informations sur les activités de marketing digital"""
        answer = """
## 📱 Activités éligibles au statut auto-entrepreneur en marketing digital

### Activités typiques
- 🎯 Gestion de campagnes publicitaires (Google Ads, Meta Ads, LinkedIn Ads)
- 📝 Création de contenu pour réseaux sociaux
- 🔍 Stratégie SEO / référencement naturel
- ✉️ Email marketing et newsletter
- 💬 Community management
- 🌐 Création de sites web (WordPress, Webflow, Shopify)
- 📊 Conseil en stratégie marketing

### Obligations légales
- 📄 Devis obligatoire pour prestations > 100€
- 🧾 Facture obligatoire pour toute prestation
- 📋 CGV à fournir avant toute prestation
- 🔒 Conformité RGPD si collecte de données

### Tarifs recommandés (débutant)
| Prestation | Tarif junior | Tarif confirmé |
|:---|:---:|:---:|
| Campagne Google Ads | 300-500€/mois | 800-1500€/mois |
| Stratégie SEO | 500-1000€ | 1500-3000€ |
| Community management | 300-600€/mois | 800-1200€/mois |
| Création site vitrine | 800-1500€ | 2000-5000€ |

### 💡 Conseil
Spécialisez-vous ! Un expert SEO ou Google Ads gagne plus qu'un généraliste.
"""
        return EntrepreneurResponse(
            answer=answer,
            sources=["urssaf.fr", "bpifrance.fr"],
            confidence=0.9
        )
    
    def _info_aides(self) -> EntrepreneurResponse:
        """Informations sur les aides financières"""
        answer = """
## 💰 Aides pour auto-entrepreneur (2026)

### ACRE (Aide à la Création ou Reprise d'Entreprise)
- ✅ **Exonération de 50%** des cotisations sociales la 1ère année
- ✅ Conditions : jeune (<30 ans), demandeur d'emploi, bénéficiaire du RSA
- 📝 À demander lors de la création

### NACRE (Nouvel Accompagnement)
- 💶 **Prêt à taux 0** jusqu'à 30 000€
- 🤝 Accompagnement personnalisé (2 ans)
- 📝 Pour projets innovants ou créateurs sans apport

### Bourse French Tech
- 💶 Jusqu'à **30 000€** pour les projets numériques innovants
- 📝 Candidature sur frenchtech.gouv.fr

### Nouveautés 2026
- 💶 **Prime numérique** : 5 000€ pour les auto-entrepreneurs du digital
- 📊 **Crédit d'impôt formation** : 50% des frais de formation (plafond 1000€/an)

### Comment demander ?
1. Créez votre auto-entreprise
2. Renseignez votre éligibilité sur le guichet unique
3. Déposez un dossier sur bpifrance-creation.fr
"""
        return EntrepreneurResponse(
            answer=answer,
            sources=["bpifrance-creation.fr", "frenchtech.gouv.fr", "service-public.fr"],
            confidence=0.9
        )
    
    def _guide_general(self) -> EntrepreneurResponse:
        """Guide général"""
        answer = """
## 🚀 Guide pour devenir auto-entrepreneur

### Résumé en 3 points

1. **Éligibilité** : 18 ans, toute activité non réglementée
2. **Formalités** : Déclaration sur guichet unique (15 min)
3. **Gestion** : Déclarer CA mensuel ou trimestriel

### Pourquoi choisir ce statut ?
- ✅ Formalités simplifiées
- ✅ Paiement des cotisations au réel du CA
- ✅ TVA non applicable si CA < seuils
- ✅ Comptabilité allégée

### Limitations
- ⚠️ Plafond CA à 77 700€ pour les services
- ⚠️ Cotisations plus élevées que régime réel (21.2%)
- ⚠️ Pas de déduction de charges

### 💡 Pour aller plus loin
Posez-moi des questions précises comme :
- "Quelles sont les étapes pour devenir auto-entrepreneur ?"
- "Comment déclarer mon chiffre d'affaires ?"
- "Quelles aides pour les jeunes diplômés ?"
"""
        return EntrepreneurResponse(
            answer=answer,
            sources=["service-public.fr", "urssaf.fr"],
            confidence=0.85
        )


_entrepreneur_tool = None


def get_entrepreneur_tool() -> EntrepreneurTool:
    """Singleton"""
    global _entrepreneur_tool
    if _entrepreneur_tool is None:
        _entrepreneur_tool = EntrepreneurTool()
    return _entrepreneur_tool