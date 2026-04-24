"""
Tool unique pour l'assistant - Combine RAG + Conseils métiers + Juridique
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AssistantResponse:
    answer: str
    confidence: float
    category: str


class ComprehensiveTool:
    """Tool unique qui fait tout"""
    
    def __init__(self):
        logger.info("ComprehensiveTool initialisé")
    
    def detect_intent(self, query: str) -> Tuple[str, Optional[str]]:
        """Détecte le type de question et le métier"""
        q = query.lower()
        
        # Dictionnaire métier -> mots-clés (ordre important)
        metiers_map = {
            "plombier": ["plombier", "plomberie", "sanitaire", "chauffage", "canalisation"],
            "electricien": ["électricien", "electricien", "elec", "électricité", "câblage"],
            "menuisier": ["menuisier", "menuiserie", "ébéniste", "bois", "agencement"],
            "formateur": ["formateur", "professeur", "enseignant", "pédagogie", "formation"],
            "photographe": ["photographe", "photo", "portrait", "mariage", "cliché"],
            "consultant": ["consultant", "conseil", "stratégie", "consulting"],
            "commercial": ["commercial", "vente", "business", "prospection"],
            "developpeur": ["développeur", "dev", "programmeur", "code", "python", "javascript"]
        }
        
        # Parcourir tous les métiers
        for metier, keywords in metiers_map.items():
            for keyword in keywords:
                if keyword in q:
                    logger.info(f"Métier détecté: {metier}")
                    return ("metier", metier)
        
        # Autres intentions
        if any(x in q for x in ["plan de vigilance", "commissaire aux comptes"]):
            return ("seuil", None)
        
        if any(x in q for x in ["statut", "auto-entrepreneur", "eurl", "sasu", "aide", "acre"]):
            return ("conseil", None)
        
        if re.search(r'[LAD]\.\s*\d{1,3}(?:[-.]\d{1,3})?', q):
            return ("article", None)
        
        return ("general", None)
    
    def answer(self, query: str) -> AssistantResponse:
        intent, value = self.detect_intent(query)
        
        if intent == "metier":
            return self._answer_metier(value)
        elif intent == "seuil":
            return self._answer_seuil(query)
        elif intent == "conseil":
            return self._answer_conseil(query)
        elif intent == "article":
            return self._answer_article(query)
        else:
            return self._answer_general()
    
    def _answer_metier(self, metier: str) -> AssistantResponse:
        # Données détaillées par métier
        metiers_data = {
            "plombier": {
                "titre": "Plombier indépendant",
                "statut": "Auto-entrepreneur ou EURL",
                "formation": "CAP Plomberie (2 ans)",
                "salaire": "2500-3500€/mois",
                "secteurs": "Bâtiment, Particuliers, PME",
                "etapes": [
                    "Obtenir un CAP Plomberie",
                    "Travailler 1-2 ans en entreprise",
                    "S'inscrire comme auto-entrepreneur",
                    "Investir dans l'outillage (3000-8000€)",
                    "S'assurer (RC Pro, décennale)"
                ]
            },
            "electricien": {
                "titre": "Électricien indépendant",
                "statut": "Auto-entrepreneur ou EURL",
                "formation": "CAP Électricien (2 ans)",
                "salaire": "2500-4000€/mois",
                "secteurs": "Bâtiment, Particuliers, PME",
                "etapes": [
                    "Obtenir un CAP Électricien",
                    "Obtenir l'habilitation électrique",
                    "Travailler 1-2 ans en entreprise",
                    "S'inscrire comme auto-entrepreneur",
                    "Investir dans l'outillage"
                ]
            },
            "menuisier": {
                "titre": "Menuisier indépendant",
                "statut": "Auto-entrepreneur ou EURL",
                "formation": "CAP Menuisier (2 ans)",
                "salaire": "2000-3000€/mois",
                "secteurs": "Bâtiment, Particuliers, Agencement",
                "etapes": [
                    "Obtenir un CAP Menuisier",
                    "Travailler 1-2 ans en entreprise",
                    "Créer un portfolio de vos réalisations",
                    "S'inscrire comme auto-entrepreneur",
                    "Équiper un atelier",
                    "Prospecter les particuliers et professionnels"
                ]
            },
            "formateur": {
                "titre": "Formateur indépendant",
                "statut": "Auto-entrepreneur",
                "formation": "BAC+3/5 + Certificat RNCP",
                "salaire": "2000-4000€/mois",
                "secteurs": "Formation pro, Organismes, E-learning",
                "etapes": [
                    "Obtenir la certification RNCP de formateur",
                    "Définir son domaine d'expertise",
                    "S'inscrire comme auto-entrepreneur (APE 8559A)",
                    "Contacter les OPCO",
                    "Créer ses modules de formation"
                ]
            },
            "photographe": {
                "titre": "Photographe professionnel",
                "statut": "Auto-entrepreneur",
                "formation": "BTS Photographie ou autodidacte",
                "salaire": "2000-4000€/mois",
                "secteurs": "Mariage, Portrait, Produit, Événementiel",
                "etapes": [
                    "Constituer un book photo",
                    "Choisir sa spécialité",
                    "Investir dans le matériel",
                    "Créer un site/Instagram",
                    "Prospecter gratuitement pour se faire connaître"
                ]
            },
            "consultant": {
                "titre": "Consultant indépendant",
                "statut": "SASU ou EURL",
                "formation": "BAC+5 (Master, École)",
                "salaire": "4000-7000€/mois",
                "secteurs": "Stratégie, RH, Digital, Finance",
                "etapes": [
                    "Acquérir 3-5 ans d'expérience",
                    "Définir son domaine d'expertise",
                    "Créer son statut (SASU recommandée)",
                    "Développer son réseau LinkedIn"
                ]
            },
            "commercial": {
                "titre": "Commercial indépendant",
                "statut": "Auto-entrepreneur ou SASU",
                "formation": "BTS NDRC ou école de commerce",
                "salaire": "2000-10000€/mois (commission)",
                "secteurs": "B2B, Tech, Industrie, Services",
                "etapes": [
                    "Maîtriser les techniques de vente",
                    "Définir sa zone et son secteur",
                    "Utiliser LinkedIn Sales Navigator",
                    "Construire un portefeuille client"
                ]
            },
            "developpeur": {
                "titre": "Développeur freelance",
                "statut": "Auto-entrepreneur (CA max 77700€)",
                "formation": "Bootcamp (3-6 mois) ou BTS/DUT",
                "salaire": "2500-5000€/mois débutant",
                "secteurs": "Tech, Startups, E-commerce, Banque",
                "etapes": [
                    "Se former (OpenClassrooms, Le Wagon)",
                    "Créer un portfolio GitHub",
                    "Faire ses premières missions sur Malt",
                    "Augmenter son TJM progressivement"
                ]
            }
        }
        
        data = metiers_data.get(metier, metiers_data.get("developpeur"))
        
        answer = f"""
## 💼 {data['titre']}

### 📋 Statut recommandé
{data['statut']}

### 🎓 Formation recommandée
{data['formation']}

### 💰 Salaire estimé
{data['salaire']}

### 🏢 Secteurs d'activité
{data['secteurs']}

### 📝 Étapes pour se lancer
"""
        for i, etape in enumerate(data['etapes'], 1):
            answer += f"{i}. {etape}\n"
        
        answer += """
### 💡 Conseil personnalisé
Commencez par une mission en parallèle de votre emploi pour tester le marché.
"""
        return AssistantResponse(answer, confidence=0.9, category="metier")
    
    def _answer_seuil(self, query: str) -> AssistantResponse:
        q = query.lower()
        
        # Extraire chiffres
        effectif = None
        ca = None
        
        eff_match = re.search(r'(\d{1,3}(?:[\s]?\d{3})*)\s*(?:salariés|employés)', q)
        if eff_match:
            effectif = int(eff_match.group(1).replace(' ', ''))
        
        ca_match = re.search(r'(\d{1,3}(?:[\s]?\d{3})*)\s*(?:millions?|M€)', q)
        if ca_match:
            ca = float(ca_match.group(1).replace(' ', '')) * 1_000_000
        
        if "vigilance" in q:
            obligation = "Établir et publier un plan de vigilance"
            article = "L.225-102-4"
            condition = "CA > 150M€ ou effectif > 5000"
            est_depasse = (effectif and effectif >= 5000) or (ca and ca >= 150_000_000)
        elif "commissaire" in q:
            obligation = "Nommer un commissaire aux comptes"
            article = "L.227-9-1"
            condition = "CA > 8M€ ou effectif > 50 (2 ans consécutifs)"
            est_depasse = (effectif and effectif >= 50) or (ca and ca >= 8_000_000)
        else:
            obligation = "Établir un plan de vigilance"
            article = "L.225-102-4"
            condition = "CA > 150M€ ou effectif > 5000"
            est_depasse = False
        
        if est_depasse:
            answer = f"⚠️ **Oui**, votre entreprise doit {obligation} (article {article})\n\n"
        else:
            answer = f"✅ **Non**, votre entreprise n'est pas concernée par {obligation}\n\n"
        
        answer += f"**Condition :** {condition}\n"
        if effectif:
            answer += f"**Votre effectif :** {effectif} salariés\n"
        if ca:
            answer += f"**Votre CA :** {ca:,.0f}€\n"
        
        return AssistantResponse(answer, confidence=0.9, category="seuil")
    
    def _answer_conseil(self, query: str) -> AssistantResponse:
        answer = """## 🚀 Guide pour se lancer

### 📋 Choix du statut juridique
- **AUTO-ENTREPRENEUR** : Plafond CA 77700€, cotisations 21.2%, comptabilité simplifiée
- **EURL** : Pas de plafond de CA, cotisations ~45%, peut déduire les charges
- **SASU** : Pas de plafond, protège le patrimoine, statut d'assimilé salarié

### 💰 Aides disponibles
- **ACRE** : Exonération de 50% des charges la 1ère année
- **NACRE** : Prêt à taux zéro jusqu'à 30000€
- **PÔLE EMPLOI** : Aide à la création jusqu'à 10000€

### 📝 Démarches générales
1. Définir son projet et son marché
2. Choisir son statut juridique
3. S'inscrire sur formalites.entreprises.gouv.fr
4. Ouvrir un compte bancaire professionnel
5. Souscrire aux assurances nécessaires
6. Développer sa clientèle
"""
        return AssistantResponse(answer, confidence=0.8, category="conseil")
    
    def _answer_article(self, query: str) -> AssistantResponse:
        match = re.search(r'([LAD]\.?\s*\d{1,3}(?:[-.]\d{1,3}){0,2})', query, re.IGNORECASE)
        if not match:
            return AssistantResponse(
                "Veuillez préciser l'article (ex: L.225-102-4)",
                confidence=0.5,
                category="article"
            )
        
        article = match.group(1).replace(' ', '').upper()
        contenu = {
            "L.225-102-4": "Devoir de vigilance : sociétés de plus de 5000 salariés ou CA > 150M€ doivent établir un plan de vigilance.",
            "L.227-9-1": "Commissaire aux comptes obligatoire pour CA > 8M€ ou effectif > 50 sur 2 ans consécutifs.",
            "L.233-16": "Obligation d'établir des comptes consolidés pour les groupes."
        }
        texte = contenu.get(article, "Article non trouvé dans la base.")
        
        return AssistantResponse(f"📜 **Article {article}**\n\n{texte}", confidence=0.9, category="article")
    
    def _answer_general(self) -> AssistantResponse:
        answer = """## 🤖 Assistant de Conformité Commerciale

Je peux vous aider sur 3 sujets :

### 1. 🛠️ Conseils métiers
- "Comment devenir **plombier** ?"
- "Conseils pour devenir **menuisier** à son compte"
- "Devenir **électricien** freelance"
- "Comment devenir **formateur** indépendant ?"
- "Devenir **photographe** professionnel"

### 2. ⚖️ Obligations légales
- "Une entreprise avec 6000 salariés doit-elle un plan de vigilance ?"
- "Que dit l'article L.225-102-4 ?"

### 3. 📝 Guides pratiques
- "Quel statut choisir pour débuter ?"
- "Quelles aides pour un jeune créateur ?"

**Posez votre question !**
"""
        return AssistantResponse(answer, confidence=0.9, category="general")


_comprehensive_tool = None


def get_comprehensive_tool():
    global _comprehensive_tool
    if _comprehensive_tool is None:
        _comprehensive_tool = ComprehensiveTool()
    return _comprehensive_tool

    # Base d'articles du Code de commerce
    ARTICLES = {
        "L.225-102-4": {
            "titre": "Devoir de vigilance des sociétés mères",
            "contenu": """I. - Les sociétés qui emploient, à la clôture de deux exercices consécutifs, 
un nombre d'au moins cinq mille salariés en France, ou un nombre d'au moins dix mille 
salariés dans le monde, et dont le chiffre d'affaires net ou le total de bilan, 
calculé sur la même période, dépasse certains seuils, établissent et mettent en œuvre 
un plan de vigilance.

II. - Le plan comporte les mesures de vigilance raisonnable propres à identifier les risques 
et à prévenir les atteintes graves envers les droits humains et les libertés fondamentales, 
la santé et la sécurité des personnes ainsi que l'environnement.

III. - Le plan et le rapport de mise en œuvre sont rendus publics et déposés au greffe.""",
            "source": "Code de commerce, livre II, titre II, chapitre V"
        },
        "L.227-9-1": {
            "titre": "Commissaire aux comptes dans les SAS",
            "contenu": """Dans les sociétés par actions simplifiées, le contrôle des comptes est exercé 
par un ou plusieurs commissaires aux comptes dans les conditions prévues à l'article L. 227-9.
La nomination d'un commissaire aux comptes est obligatoire lorsque la société dépasse les seuils 
fixés par décret en Conseil d'État pour deux exercices consécutifs.""",
            "source": "Code de commerce, livre II, titre II, chapitre VII"
        },
        "L.233-16": {
            "titre": "Comptes consolidés",
            "contenu": """Les sociétés qui contrôlent exclusivement ou conjointement une ou plusieurs entreprises 
sont tenues d'établir et de publier des comptes consolidés ainsi qu'un rapport sur la gestion du groupe.
Cette obligation s'applique aux sociétés qui dépassent certains seuils fixés par décret.""",
            "source": "Code de commerce, livre II, titre III, chapitre III"
        }
    }
    
    def _answer_article(self, query: str) -> AssistantResponse:
        """Recherche et répond sur un article du Code de commerce"""
        # Extraire la référence d'article
        match = re.search(r'([LAD]\.?\s*\d{1,3}(?:[-.]\d{1,3}){0,2})', query, re.IGNORECASE)
        if not match:
            return AssistantResponse(
                self._answer_general().answer,
                confidence=0.5,
                category="article"
            )
        
        article_ref = match.group(1).replace(' ', '').upper()
        
        # Chercher l'article dans la base
        if article_ref in self.ARTICLES:
            article = self.ARTICLES[article_ref]
            answer = f"""
## 📜 **Article {article_ref}** - {article['titre']}

{article['contenu']}

---
**Source :** {article['source']}
**Mise à jour :** Code de commerce édition 2026-04-15
"""
            return AssistantResponse(answer, confidence=0.95, category="article")
        else:
            # Article non trouvé - proposer une recherche
            return AssistantResponse(
                f"""
## ❓ Article {article_ref} non trouvé

Je ne dispose pas encore du texte complet de l'article {article_ref} dans ma base.

### 📚 Articles disponibles actuellement :
- L.225-102-4 : Devoir de vigilance
- L.227-9-1 : Commissaire aux comptes
- L.233-16 : Comptes consolidés

### 💡 Suggestions :
- Vérifiez la référence (ex: L.225-102-4)
- Consultez le Code sur [Légifrance](https://www.legifrance.gouv.fr/codes/id/LEGITEXT000005634379/)
""",
                confidence=0.6,
                category="article"
            )
