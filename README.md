# ⚖️ Assistant de Conformité Commerciale

Assistant intelligent basé sur le **Code de commerce français** (2100+ pages, 7259 articles) utilisant l'architecture **RAG (Retrieval-Augmented Generation)** + **Agent**.

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|:---|:---|
| 🔍 **Recherche RAG** | Recherche vectorielle dans l'intégralité du Code de commerce |
| 📜 **Résolution de citations** | Détection automatique des articles (ex: L.225-102-4) |
| 📊 **Vérification de seuils** | Calcul automatique des obligations (CA, effectif, bilan) |
| ⚖️ **Jurisprudence** | Recherche de décisions de justice via Judilibre |
| 💼 **Guide métiers** | Conseils détaillés pour devenir indépendant (plombier, electricien, formateur, consultant) |
| 💬 **Chat conversationnel** | Interface Streamlit avec historique |

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Raoul-Fossua/compliance-assistant.git
cd compliance-assistant
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
cd src
streamlit run app_streamlit.py
```

L'application est accessible sur `http://localhost:8501`

## 💬 Exemples de questions

| Catégorie | Question |
|:---|:---|
| **Code commerce** | `Que dit l'article L.225-102-4 ?` |
| **Seuil** | `Une entreprise avec 6000 salariés doit-elle un plan de vigilance ?` |
| **Jurisprudence** | `Jurisprudence sur le devoir de vigilance` |
| **Métier** | `comment devenir plombier à son compte ?` |
| **Métier** | `comment devenir formateur indépendant ?` |
| **Métier** | `conseils pour devenir electricien en freelance` |
| **Métier** | `comment devenir consultant à son compte` |

## 📁 Structure du projet

```
compliance-assistant/
│
├── src/
│   ├── app_streamlit.py          # Interface utilisateur
│   ├── agents/
│   │   ├── agent.py              # Agent conversationnel
│   │   └── router.py             # Routeur intelligent
│   ├── tools/
│   │   ├── tools.py              # Outils principaux
│   │   ├── rag_tool.py           # Outil RAG
│   │   ├── judilibre_tool.py     # Outil jurisprudence
│   │   └── metier_tool.py        # Outil guides métiers
│   └── rag/
│       └── ingest_comlex.py      # Ingestion du Code
│
├── data/                         # PDFs sources
├── chroma_db/                    # Base vectorielle
├── requirements.txt
├── .env
└── README.md
```

## 🛠️ Technologies utilisées

| Catégorie | Technologies |
|:---|:---|
| **Langage** | Python 3.10+ |
| **Framework RAG** | LangChain, Chroma DB |
| **Embeddings** | Sentence Transformers |
| **LLM** | Flan-T5-large (local) |
| **Interface** | Streamlit |
| **APIs** | Judilibre |

## ⚠️ Avertissement juridique

Cet assistant fournit des informations générales à partir de textes de loi. Il ne remplace pas un avocat ou un juriste professionnel.

## 🔧 Première utilisation après clonage

Après avoir cloné le dépôt, vous devez reconstruire la base vectorielle localement :

```bash
python src/rag/ingest_comlex.py
---


---

## 🚀 Commandes finales à exécuter

```bash
# 1. Exclure chroma_db
git rm -r --cached chroma_db/
echo "chroma_db/" >> .gitignore

# 2. Commiter
git add .gitignore
git commit -m "Exclure la base vectorielle locale"

# 3. Pousser
git push origin main


[![GitHub stars](https://img.shields.io/github/stars/Raoul-Fossua/compliance-assistant-v2)](https://github.com/Raoul-Fossua/compliance-assistant-v2/stargazers)
[![Docker Pulls](https://img.shields.io/docker/pulls/rfossuatindo/compliance-assistant)](https://hub.docker.com/r/rfossuatindo/compliance-assistant)

*Dernière mise à jour : 2026-04-18*
