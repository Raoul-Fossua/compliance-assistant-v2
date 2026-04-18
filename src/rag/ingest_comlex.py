"""
Ingestion du Code de commerce pour la base vectorielle
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from langchain_community.document_loaders import PyPDFium2Loader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document  # Correction importante

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = os.environ.get("COMPLIANCE_DATA_DIR", "./data")
DB_DIR = os.environ.get("COMPLIANCE_VECTOR_DB", "./chroma_db")
METADATA_DIR = os.environ.get("COMPLIANCE_METADATA_DIR", "./metadata")

for d in [DATA_DIR, DB_DIR, METADATA_DIR]:
    os.makedirs(d, exist_ok=True)

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class Article:
    """Article du Code de commerce"""
    id: str
    livre: str
    titre: str
    chapitre: str
    section: Optional[str]
    content: str
    hierarchy_path: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class HierarchicalCodeSplitter:
    """Parseur hiérarchique"""
    
    PATTERNS = {
        "livre": re.compile(r'^LIVRE\s+([IVXLCDM]+)\s*:\s*(.+)$', re.IGNORECASE),
        "titre": re.compile(r'^TITRE\s+([IVXLCDM]+)\s*:\s*(.+)$', re.IGNORECASE),
        "chapitre": re.compile(r'^Chapitre\s+([IVXLCDM]+)\s*:\s*(.+)$', re.IGNORECASE),
        "article": re.compile(r'^(?:Article\s+)?(L\.|R\.|D\.)\s*(\d{1,3}(?:[-.]\d{1,3}){0,4})', re.IGNORECASE),
    }
    
    def __init__(self):
        self.current = {"livre": "", "titre": "", "chapitre": "", "section": ""}
        self.articles: List[Article] = []
        self.current_article: Optional[Article] = None
        self.current_content: List[str] = []
    
    def parse_pdf(self, pdf_path: str) -> List[Article]:
        """Parse un PDF"""
        logger.info(f"Parsing: {pdf_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(pdf_path):
            logger.warning(f"Fichier non trouvé: {pdf_path}")
            return []
        
        loader = PyPDFium2Loader(pdf_path)
        pages = loader.load()
        
        for page in pages:
            self._parse_page(page.page_content)
        
        self._save_current_article()
        logger.info(f"Extrait {len(self.articles)} articles")
        return self.articles
    
    def _parse_page(self, text: str):
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            m = self.PATTERNS["livre"].match(line)
            if m:
                self._save_current_article()
                self.current["livre"] = m.group(2)
                continue
            
            m = self.PATTERNS["titre"].match(line)
            if m:
                self._save_current_article()
                self.current["titre"] = m.group(2)
                continue
            
            m = self.PATTERNS["chapitre"].match(line)
            if m:
                self._save_current_article()
                self.current["chapitre"] = m.group(2)
                continue
            
            m = self.PATTERNS["article"].match(line)
            if m:
                self._save_current_article()
                article_id = f"{m.group(1)}.{m.group(2)}"
                self.current_article = Article(
                    id=article_id,
                    livre=self.current["livre"],
                    titre=self.current["titre"],
                    chapitre=self.current["chapitre"],
                    section=None,
                    content="",
                    hierarchy_path=self._get_hierarchy_path()
                )
                self.current_content = []
                continue
            
            if self.current_article:
                self.current_content.append(line)
    
    def _get_hierarchy_path(self) -> str:
        parts = [p for p in [self.current["livre"], self.current["titre"], 
                              self.current["chapitre"]] if p]
        return " > ".join(parts)
    
    def _save_current_article(self):
        if self.current_article and self.current_content:
            self.current_article.content = "\n".join(self.current_content)
            self.articles.append(self.current_article)
            self.current_article = None
            self.current_content = []


class ArticleIndexer:
    """Index des articles"""
    
    def __init__(self, index_path: str = None):
        self.index_path = index_path or os.path.join(METADATA_DIR, "articles_index.json")
        self.articles: Dict[str, Article] = {}
        self.variations: Dict[str, str] = {}
        self._load_static_articles()
    
    def _load_static_articles(self):
        """Articles statiques pour développement"""
        self.articles = {
            "L.225-102-4": Article(
                id="L.225-102-4",
                livre="LIVRE II",
                titre="TITRE II",
                chapitre="Chapitre V",
                section="Section 2",
                content="""I. - Les sociétés qui emploient, à la clôture de deux exercices consécutifs, 
un nombre d'au moins cinq mille salariés en France, ou un nombre d'au moins dix mille 
salariés dans le monde, établissent et mettent en œuvre un plan de vigilance.

II. - Le plan comporte les mesures de vigilance raisonnable propres à identifier les risques 
et à prévenir les atteintes graves envers les droits humains.""",
                hierarchy_path="LIVRE II > TITRE II > Chapitre V > Section 2"
            ),
            "L.230-1": Article(
                id="L.230-1",
                livre="LIVRE II",
                titre="TITRE III",
                chapitre="Chapitre préliminaire",
                section=None,
                content="""Les sociétés sont réparties en différentes catégories selon leur taille.
Seuils : total bilan 20M€, CA 40M€, effectif 250 salariés.""",
                hierarchy_path="LIVRE II > TITRE III > Chapitre préliminaire"
            ),
            "L.227-9-1": Article(
                id="L.227-9-1",
                livre="LIVRE II",
                titre="TITRE II",
                chapitre="Chapitre VII",
                section=None,
                content="""La nomination d'un commissaire aux comptes est obligatoire lorsque 
la société dépasse les seuils fixés par décret (CA > 8M€ ou effectif > 50).""",
                hierarchy_path="LIVRE II > TITRE II > Chapitre VII"
            )
        }
        
        for aid in self.articles:
            self.variations[aid] = aid
            self.variations[aid.replace('.', '-')] = aid
            self.variations[aid.lower()] = aid
            self.variations[f"Article {aid}"] = aid
    
    def resolve(self, citation: str) -> Optional[Article]:
        """Résout une citation"""
        if not citation:
            return None
        citation = citation.strip().upper()
        if citation in self.articles:
            return self.articles[citation]
        if citation in self.variations:
            return self.articles.get(self.variations[citation])
        return None
    
    def save(self):
        """Sauvegarde l'index"""
        data = {
            "articles": {aid: art.to_dict() for aid, art in self.articles.items()},
            "variations": self.variations,
            "updated_at": datetime.now().isoformat()
        }
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class ComplianceVectorStore:
    """Vector store"""
    
    def __init__(self, persist_dir: str = DB_DIR):
        self.persist_dir = persist_dir
        self.embeddings = None
        self.vectorstore = None
        self.article_indexer = ArticleIndexer()
        self._init_embeddings()
    
    def _init_embeddings(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
            logger.info("Embeddings initialisés")
        except Exception as e:
            logger.warning(f"Erreur embeddings: {e}")
            self.embeddings = None
    
    def build(self, pdf_paths: List[str] = None) -> Optional[Chroma]:
        """Construit la base vectorielle"""
        all_articles = []
        splitter = HierarchicalCodeSplitter()
        
        if pdf_paths:
            for path in pdf_paths:
                if os.path.exists(path):
                    all_articles.extend(splitter.parse_pdf(path))
                else:
                    logger.warning(f"Fichier non trouvé: {path}")
        else:
            for file in os.listdir(DATA_DIR):
                if file.lower().endswith(".pdf"):
                    pdf_path = os.path.join(DATA_DIR, file)
                    all_articles.extend(splitter.parse_pdf(pdf_path))
        
        if not all_articles:
            logger.warning("Aucun article trouvé, utilisation des articles statiques")
            # Utiliser les articles statiques
            all_articles = list(self.article_indexer.articles.values())
        
        documents = []
        for article in all_articles:
            doc = Document(
                page_content=article.content,
                metadata={
                    "article_id": article.id,
                    "hierarchy_path": article.hierarchy_path,
                    "livre": article.livre,
                    "chapitre": article.chapitre
                }
            )
            documents.append(doc)
        
        if not documents:
            logger.error("Aucun document à indexer")
            return None
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        self.vectorstore.persist()
        logger.info(f"Vector store créé: {self.persist_dir} avec {len(documents)} documents")
        return self.vectorstore
    
    def load(self) -> Optional[Chroma]:
        """Charge la base existante"""
        if not self.embeddings:
            return None
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
            logger.info(f"Vector store chargé: {self.persist_dir}")
            return self.vectorstore
        except Exception as e:
            logger.warning(f"Erreur chargement: {e}")
            return None


def build_vectorstore(pdf_paths: List[str] = None):
    """Construction principale"""
    vstore = ComplianceVectorStore()
    return vstore.build(pdf_paths)


if __name__ == "__main__":
    build_vectorstore()