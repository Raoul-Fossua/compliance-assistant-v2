"""
Tool générique pour les conseils métier
Avec réponses détaillées pour les jeunes diplômés
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetierResponse:
    answer: str
    sources: List[str]
    confidence: float
    domain: str


class MetierTool:
    
    # Base de connaissances complète et détaillée
    METIER_DATA = {
        "plombier": {
            "titre": "Devenir plombier indépendant",
            "description": "Le métier de plombier consiste à installer, réparer et entretenir les systèmes de plomberie, chauffage et sanitaire.",
            "formations": [
                "CAP Plomberie (2 ans) - Accessible après la 3ème",
                "BP Plomberie (2 ans) - Après CAP",
                "Bac Pro Technicien en installations des systèmes énergétiques et climatiques (3 ans)",
                "Mention Complémentaire (1 an) pour se spécialiser"
            ],
            "pour_jeune_diplome": "Si vous sortez d'un CAP ou BAC Pro plomberie, vous pouvez directement vous inscrire comme auto-entrepreneur. Le salaire moyen d'un jeune plombier est de 2000-2500 euros par mois.",
            "statut": "Auto-entrepreneur recommandé pour démarrer (CA max 77700 euros). Au-delà, passer en EURL.",
            "tarifs": [
                "Debutant (0-2 ans) : 35-50 euros par heure",
                "Confirme (2-5 ans) : 50-65 euros par heure",
                "Expert (5+ ans) : 65-90 euros par heure"
            ],
            "revenus_mensuels": "Un plombier indépendant débutant peut espérer 2500-3500 euros par mois après charges.",
            "investissement": "Comptez 3000-8000 euros d'outillage pour démarrer (perceuse, cintreuse, poste à souder, etc.).",
            "assurances": [
                "Responsabilite Civile Professionnelle (RC Pro) : 300-600 euros par an",
                "Garantie Decennale (obligatoire) : 800-1500 euros par an"
            ],
            "etapes": [
                "1️⃣ Obtenir un diplome : CAP ou BAC Pro plomberie (2-3 ans)",
                "2️⃣ Acquérir de l'experience : 1-2 ans en tant que salarie",
                "3️⃣ Choisir son statut : Auto-entrepreneur pour démarrer",
                "4️⃣ S'inscrire au guichet unique : formalites.entreprises.gouv.fr",
                "5️⃣ Investir dans l'outillage : 3000-8000 euros",
                "6️⃣ Souscrire aux assurances : RC Pro et Decennale",
                "7️⃣ Trouver ses premiers clients : bouche-a-oreille, 123devis, Travaux.com"
            ],
            "aides": [
                "ACRE : Exoneration de 50 pourcent des charges la 1ère année",
                "NACRE : Pret à taux 0 jusqu'à 30 000 euros",
                "Aide à la creation (Pole emploi) : jusqu'à 10 000 euros"
            ],
            "plateformes": ["123devis", "Travaux.com", "Artisan français", "LinkedIn", "Facebook local"],
            "sites_officiels": [
                "https://formalites.entreprises.gouv.fr",
                "https://www.urssaf.fr",
                "https://www.service-public.fr",
                "https://www.bpifrance-creation.fr"
            ]
        },
        "electricien": {
            "titre": "Devenir electricien indépendant",
            "description": "L'electricien installe, depanne et entretient les installations électriques (maisons, appartements, entreprises).",
            "formations": [
                "CAP Electricien (2 ans)",
                "Bac Pro Metiers de l'electricite (3 ans)",
                "BTS Electrotechnique (2 ans après BAC)",
                "Habilitation electrique (obligatoire pour travailler)"
            ],
            "pour_jeune_diplome": "Avec un CAP ou BAC Pro electricite, vous pouvez commencer comme auto-entrepreneur. Le salaire d'un jeune electricien est de 2000-2800 euros par mois.",
            "statut": "Auto-entrepreneur pour CA inferieur à 77700 euros, EURL au-dela",
            "tarifs": [
                "Debutant : 35-55 euros par heure",
                "Confirme : 55-70 euros par heure",
                "Expert : 70-90 euros par heure"
            ],
            "revenus_mensuels": "2500-4000 euros par mois pour un electricien indépendant débutant.",
            "investissement": "Comptez 2000-5000 euros d'outillage (multimètre, perceuse, pinces, etc.).",
            "assurances": [
                "Responsabilite Civile Professionnelle : 300-500 euros par an",
                "Garantie Decennale : 600-1200 euros par an"
            ],
            "etapes": [
                "1️⃣ Obtenir un diplome : CAP ou BAC Pro electricite",
                "2️⃣ Obtenir l'habilitation electrique (obligatoire)",
                "3️⃣ Faire 1-2 ans en entreprise pour apprendre",
                "4️⃣ Choisir le statut auto-entrepreneur",
                "5️⃣ S'inscrire au guichet unique",
                "6️⃣ Acheter son outillage",
                "7️⃣ S'assurer et prospecter"
            ],
            "aides": ["ACRE", "NACRE", "Aide Pole emploi", "Pret d'honneur Initiative France"],
            "plateformes": ["123devis", "Travaux.com", "LinkedIn", "Facebook"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr", "https://www.urssaf.fr"]
        },
        "menuisier": {
            "titre": "Devenir menuisier indépendant",
            "description": "Le menuisier fabrique, installe et repare des ouvrages en bois (portes, fenetres, escaliers, meubles).",
            "formations": [
                "CAP Menuisier (2 ans)",
                "CAP Menuisier fabricant (2 ans)",
                "BP Menuiserie (2 ans après CAP)",
                "Bac Pro Technicien menuisier (3 ans)"
            ],
            "pour_jeune_diplome": "CAP menuiserie en poche, vous pouvez vous lancer. Attention : prévoyez un atelier ou un local pour travailler.",
            "statut": "Auto-entrepreneur pour débuter",
            "tarifs": [
                "Debutant : 35-55 euros par heure",
                "Confirme : 55-75 euros par heure",
                "Expert : 75-100 euros par heure"
            ],
            "revenus_mensuels": "Un menuisier débutant gagne 2000-3000 euros par mois.",
            "investissement": "Atelier plus outils : 5000-20000 euros (scie, dégauchisseuse, toupie, etc.)",
            "assurances": ["RC Pro (300-600 euros par an)", "Decennale (800-1500 euros par an)"],
            "etapes": [
                "1️⃣ Obtenir un CAP Menuisier",
                "2️⃣ Se specialiser (agencement, fabrication, installation)",
                "3️⃣ Creer un portfolio de vos realisations",
                "4️⃣ S'inscrire comme auto-entrepreneur",
                "5️⃣ Equiper un atelier",
                "6️⃣ Prospecter les particuliers et professionnels"
            ],
            "aides": ["ACRE", "NACRE", "Aide à la creation"],
            "plateformes": ["123devis", "Travaux.com", "Artisan français", "Instagram"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr"]
        },
        "charpentier": {
            "titre": "Devenir charpentier indépendant",
            "description": "Le charpentier construit et installe les charpentes en bois pour les maisons et bâtiments.",
            "formations": [
                "CAP Charpentier bois (2 ans)",
                "BP Charpentier (2 ans après CAP)",
                "Bac Pro Technicien charpentier (3 ans)"
            ],
            "pour_jeune_diplome": "Metier physique et technique. Un CAP charpentier suffit pour débuter. Le salaire est attractif.",
            "statut": "Auto-entrepreneur ou EURL",
            "tarifs": [
                "Debutant : 40-60 euros par heure",
                "Confirme : 60-85 euros par heure",
                "Expert : 85-120 euros par heure"
            ],
            "revenus_mensuels": "2500-4000 euros par mois pour un charpentier débutant.",
            "investissement": "Outillage : 5000-15000 euros (scie circulaire, marteau pneumatique, niveau laser, etc.)",
            "assurances": ["RC Pro (400-700 euros par an)", "Decennale (1000-2000 euros par an)"],
            "etapes": [
                "1️⃣ CAP Charpentier (obligatoire)",
                "2️⃣ Travailler 2 ans en entreprise",
                "3️⃣ Investir dans l'outillage",
                "4️⃣ S'inscrire au guichet unique",
                "5️⃣ Se faire connaître des entreprises du BTP",
                "6️⃣ S'assurer (RC Pro et decennale)"
            ],
            "aides": ["ACRE", "NACRE", "Aide BTP creation"],
            "plateformes": ["123devis", "Travaux.com", "LinkedIn"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr"]
        },
        "formateur": {
            "titre": "Devenir formateur indépendant",
            "description": "Le formateur transmet ses compétences à des adultes en formation professionnelle.",
            "formations": [
                "Diplome dans votre domaine d'expertise",
                "Titre de formateur professionnel (RNCP niveau 6) - OBLIGATOIRE",
                "Master MEEF (enseignement)",
                "Certificat de compétence pédagogique"
            ],
            "pour_jeune_diplome": "Ideal si vous avez un BAC+3/5 et une envie de transmettre. La certification RNCP est un investissement rentable.",
            "statut": "Auto-entrepreneur (code APE 8559A)",
            "tarifs": [
                "Debutant : 300-500 euros par jour",
                "Confirme : 500-700 euros par jour",
                "Expert : 700-1000 euros par jour"
            ],
            "revenus_mensuels": "Un formateur débutant peut gagner 2000-4000 euros par mois.",
            "investissement": "Formation certifiante RNCP : 3000-8000 euros. Matériel : ordinateur, vidéoprojecteur.",
            "obligations": [
                "Certification RNCP obligatoire (depuis 2021)",
                "Declaration d'activite à la DREETS",
                "Label Qualiopi pour les financements CPF"
            ],
            "etapes": [
                "1️⃣ Avoir un diplome dans votre domaine (BAC+3 minimum)",
                "2️⃣ Obtenir la certification RNCP de formateur",
                "3️⃣ Creer vos modules de formation",
                "4️⃣ S'inscrire comme auto-entrepreneur (APE 8559A)",
                "5️⃣ Declarer votre activité à la DREETS",
                "6️⃣ Contacter les OPCO (financements)",
                "7️⃣ Proposer des formations en entreprise"
            ],
            "aides": ["ACRE", "Aide au conseil (BPI)", "Pret d'honneur"],
            "plateformes": ["Malt", "Comet", "Kelformation", "LinkedIn"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr", "https://www.urssaf.fr"]
        },
        "consultant": {
            "titre": "Devenir consultant indépendant",
            "description": "Le consultant apporte son expertise pour aider les entreprises à résoudre des problèmes ou améliorer leurs performances.",
            "formations": [
                "BAC+5 (Master, Ecole de commerce, Ingenieur)",
                "Specialisation : stratégie, RH, digital, finance",
                "Certifications selon le domaine"
            ],
            "pour_jeune_diplome": "Ideal avec un BAC+5. Commencez en freelance tout en gardant un emploi pour vous faire un réseau.",
            "statut": "SASU ou EURL recommandé (crédibilité)",
            "tarifs": [
                "Junior (0-3 ans) : 400-600 euros par jour",
                "Confirme (3-7 ans) : 600-900 euros par jour",
                "Senior (7+ ans) : 900-1500 euros par jour"
            ],
            "revenus_mensuels": "Un consultant junior peut espérer 4000-7000 euros par mois.",
            "investissement": "Faible (ordinateur, LinkedIn Premium, site web)",
            "etapes": [
                "1️⃣ Obtenir un BAC+5 (Master ou Ecole)",
                "2️⃣ Acquérir une experience en entreprise (3-5 ans)",
                "3️⃣ Definir son domaine d'expertise",
                "4️⃣ Creer son statut (SASU recommandee)",
                "5️⃣ Developper son reseau sur LinkedIn",
                "6️⃣ Proposer des missions courtes pour commencer"
            ],
            "aides": ["ACRE", "Aide au conseil BPI", "Pret d'honneur"],
            "plateformes": ["LinkedIn", "Malt", "Hopwork", "Experts-Comptables"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr", "https://www.bpifrance-creation.fr"]
        },
        "commercial": {
            "titre": "Devenir commercial indépendant",
            "description": "Le commercial indépendant prospecte, négocie et vend des produits ou services pour le compte d'entreprises clientes.",
            "formations": [
                "BAC+2 en commerce (BTS NDRC, BTS MCO)",
                "BAC+3/5 en école de commerce",
                "Formation en négociation"
            ],
            "pour_jeune_diplome": "Accessible dès un BTS. Commencez par une mission simple en portage salarial.",
            "statut": "Auto-entrepreneur ou SASU",
            "tarifs": [
                "Commission sur vente (5-15 pourcent)",
                "Forfait : 250-500 euros par jour",
                "Fixe plus commission"
            ],
            "revenus_mensuels": "Variable selon performances : 2000-10000 euros par mois.",
            "investissement": "Téléphone, ordinateur, CRM, LinkedIn Premium",
            "etapes": [
                "1️⃣ Obtenir une formation commerciale",
                "2️⃣ Definir son secteur (B2B ou B2C)",
                "3️⃣ Choisir son statut (auto-entrepreneur)",
                "4️⃣ Contacter des entreprises clientes",
                "5️⃣ Proposer une commission attractive",
                "6️⃣ Utiliser LinkedIn Sales Navigator"
            ],
            "aides": ["ACRE", "Aide à la creation"],
            "plateformes": ["LinkedIn", "Malt", "Kompass", "Societe.com"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr"]
        },
        "developpeur": {
            "titre": "Devenir développeur freelance",
            "description": "Le développeur crée des sites web, applications et logiciels pour les entreprises.",
            "formations": [
                "Bootcamp (3-6 mois) : Le Wagon, O'clock",
                "Bac+2 (BTS SIO, DUT Informatique)",
                "Bac+5 (Master, Ecole d'ingenieur)",
                "Auto-formation (OpenClassrooms, Udemy)"
            ],
            "pour_jeune_diplome": "Le freelance est accessible après 1-2 ans d'expérience en entreprise. Commencez par des petites missions.",
            "statut": "Auto-entrepreneur pour CA inferieur à 77700 euros",
            "tarifs": [
                "Junior : 250-400 euros par jour",
                "Confirme : 400-600 euros par jour",
                "Senior : 600-900 euros par jour"
            ],
            "revenus_mensuels": "Un développeur junior gagne 3000-5000 euros par mois.",
            "investissement": "Ordinateur performant (1000-3000 euros), licences, formations",
            "etapes": [
                "1️⃣ Se former (bootcamp ou auto-formation)",
                "2️⃣ Creer un portfolio GitHub",
                "3️⃣ Acquérir 1-2 ans d'experience",
                "4️⃣ S'inscrire comme auto-entrepreneur",
                "5️⃣ Definir son TJM",
                "6️⃣ Postuler sur Malt, Comet, Upwork",
                "7️⃣ Developper son reseau LinkedIn"
            ],
            "aides": ["ACRE", "Aide à la formation (CPF)", "Pret d'honneur"],
            "plateformes": ["Malt", "Comet", "Upwork", "Freelance-info", "GitHub Jobs"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr", "https://www.urssaf.fr"]
        },
        "redacteur": {
            "titre": "Devenir rédacteur web freelance",
            "description": "Le rédacteur web crée du contenu pour les sites internet (articles, fiches produits, newsletters).",
            "formations": [
                "Formation en redaction SEO (quelques centaines d'euros)",
                "Bac+2/3 en communication, journalisme",
                "Auto-formation (blogs, YouTube)"
            ],
            "pour_jeune_diplome": "Tres accessible sans diplome specifique. Commencez par un blog ou des publications sur LinkedIn.",
            "statut": "Auto-entrepreneur",
            "tarifs": [
                "Debutant : 15-25 euros par heure",
                "Confirme : 25-40 euros par heure",
                "Expert SEO : 40-70 euros par heure"
            ],
            "revenus_mensuels": "1500-3000 euros par mois pour un débutant.",
            "investissement": "Faible (ordinateur, formations SEO)",
            "etapes": [
                "1️⃣ Se former au SEO (MOZ, Semrush)",
                "2️⃣ Creer un portfolio (blog personnel)",
                "3️⃣ S'inscrire comme auto-entrepreneur",
                "4️⃣ Demarcher des agences SEO",
                "5️⃣ Proposer un article test gratuit",
                "6️⃣ Developper son reseau"
            ],
            "aides": ["ACRE", "Aide à la formation CPF"],
            "plateformes": ["Malt", "Hopwork", "ProBlogger", "LinkedIn"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr"]
        },
        "photographe": {
            "titre": "Devenir photographe professionnel",
            "description": "Le photographe réalise des photos pour des particuliers (mariage, portrait) ou des professionnels.",
            "formations": [
                "Auto-formation (YouTube, blogs)",
                "BTS Photographie (2 ans)",
                "Ecole de photographie (Speos, EFET)"
            ],
            "pour_jeune_diplome": "Le portfolio prime sur le diplome. Commencez par des photos gratuites pour vous faire connaître.",
            "statut": "Auto-entrepreneur",
            "tarifs": [
                "Debutant : 200-400 euros par jour",
                "Confirme : 400-700 euros par jour",
                "Expert : 700-1200 euros par jour"
            ],
            "revenus_mensuels": "2000-4000 euros par mois.",
            "investissement": "Materiel photo : 2000-10000 euros (boîtier, objectifs, eclairage).",
            "etapes": [
                "1️⃣ Se former (technique, retouche)",
                "2️⃣ Constituer un book photo",
                "3️⃣ Choisir sa specialite (mariage, portrait)",
                "4️⃣ Investir dans le materiel",
                "5️⃣ S'inscrire auto-entrepreneur",
                "6️⃣ Creer un site ou Instagram",
                "7️⃣ Prospecter gratuitement pour se faire connaître"
            ],
            "aides": ["ACRE", "Aide à la creation"],
            "plateformes": ["Instagram", "Facebook", "Malt", "Photo-services.net"],
            "sites_officiels": ["https://formalites.entreprises.gouv.fr"]
        }
    }
    
    def __init__(self):
        logger.info(f"MetierTool initialise avec {len(self.METIER_DATA)} metiers detailles")
    
    def answer(self, metier: str, original_query: str = "") -> MetierResponse:
        """Repond avec un guide detaille pour le metier"""
        
        # Nettoyer le metier
        metier_clean = metier.lower().strip()
        
        # Mapping des synonymes
        synonymes = {
            "plombier": ["plombier", "plomberie"],
            "electricien": ["electricien", "électricien", "elec"],
            "menuisier": ["menuisier", "menuiserie"],
            "charpentier": ["charpentier", "charpente"],
            "formateur": ["formateur", "prof", "enseignant", "formation"],
            "consultant": ["consultant", "conseil", "consulting"],
            "commercial": ["commercial", "vente", "business dev"],
            "developpeur": ["developpeur", "développeur", "dev", "programmeur"],
            "redacteur": ["redacteur", "rédacteur", "copywriter"],
            "photographe": ["photographe", "photo"]
        }
        
        # Trouver le bon metier
        found_metier = None
        for key, synonyms in synonymes.items():
            if metier_clean in synonyms or any(s in metier_clean for s in synonyms):
                found_metier = key
                break
        
        if not found_metier:
            found_metier = metier_clean
        
        data = self.METIER_DATA.get(found_metier)
        
        if not data:
            return self._fallback_response(metier)
        
        # Construire la reponse detaillee (sans backslash dans les f-strings)
        answer = "## 💼 " + data['titre'] + "\n\n"
        answer += data['description'] + "\n\n"
        
        answer += "### 🎓 Formations necessaires\n"
        for formation in data.get('formations', []):
            answer += "- " + formation + "\n"
        
        answer += "\n### 🎯 Pour un jeune diplome\n"
        answer += data.get('pour_jeune_diplome', 'Accessible apres une formation professionnelle.') + "\n\n"
        
        answer += "### 📋 Statut recommande\n"
        answer += data.get('statut', 'Auto-entrepreneur pour demarrer') + "\n\n"
        
        answer += "### 💰 Tarifs et revenus\n"
        for tarif in data.get('tarifs', []):
            answer += "- " + tarif + "\n"
        
        answer += "\n" + data.get('revenus_mensuels', '') + "\n\n"
        
        answer += "### 🛠️ Investissement de depart\n"
        answer += data.get('investissement', 'Comptez un budget pour l outillage et les assurances.') + "\n\n"
        
        answer += "### 🛡️ Assurances obligatoires\n"
        for assurance in data.get('assurances', []):
            answer += "- " + assurance + "\n"
        
        answer += "\n### 📝 Etapes pour se lancer\n"
        for etape in data.get('etapes', []):
            answer += etape + "\n"
        
        if data.get('aides'):
            answer += "\n### 💶 Aides financieres disponibles\n"
            for aide in data.get('aides', []):
                answer += "- " + aide + "\n"
        
        if data.get('plateformes'):
            answer += "\n### 🌐 Plateformes pour trouver des clients\n"
            for plateforme in data.get('plateformes', []):
                answer += "- " + plateforme + "\n"
        
        answer += "\n### 🔗 Liens utiles pour les demarches\n"
        for site in data.get('sites_officiels', [])[:3]:
            answer += "- " + site + "\n"
        
        answer += """
### 💡 Conseil personnalise
Commencez par 1-2 jours par semaine en freelance tout en gardant votre emploi pour tester le marche. Utilisez l'ACRE pour reduire vos charges la premiere annee.
"""
        
        return MetierResponse(
            answer=answer,
            sources=data.get('sites_officiels', ["service-public.fr", "bpifrance-creation.fr"]),
            confidence=0.9,
            domain=found_metier
        )
    
    def _fallback_response(self, metier: str) -> MetierResponse:
        answer = f"""
## 💼 Devenir {metier} independant

Je n'ai pas encore de guide detaille pour ce metier, mais voici les bases.

### 🎓 Formations
Recherchez sur Google : "formation pour devenir {metier}" ou "CAP {metier}"

### 📋 Statut recommande
Auto-entrepreneur pour demarrer (CA max 77700 euros)

### 📝 Demarches generales
1️⃣ Se former (diplome ou formation professionnelle)
2️⃣ Acquérir de l'experience (1-2 ans en entreprise)
3️⃣ S'inscrire au guichet unique (formalites.entreprises.gouv.fr)
4️⃣ Souscrire aux assurances (RC Pro et decennale si artisan)
5️⃣ Prospecter des clients

### 💰 Aides disponibles
- ACRE : exoneration de 50 pourcent des charges la 1ère année
- NACRE : pret à taux 0
- Aide Pole emploi (jusqu'à 10 000 euros)

### 🔗 Sites utiles
- https://formalites.entreprises.gouv.fr (creation)
- https://www.urssaf.fr (declarations)
- https://www.bpifrance-creation.fr (aides)

Precisez votre metier pour un guide plus detaille.
"""
        return MetierResponse(
            answer=answer,
            sources=["service-public.fr", "bpifrance-creation.fr"],
            confidence=0.6,
            domain=metier
        )


_metier_tool = None


def get_metier_tool() -> MetierTool:
    global _metier_tool
    if _metier_tool is None:
        _metier_tool = MetierTool()
    return _metier_tool