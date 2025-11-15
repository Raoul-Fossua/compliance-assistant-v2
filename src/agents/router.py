# src/agents/router.py

from transformers import pipeline

from rag.rag_chain import answer_with_rag
from agents.tools import (
    calculator_tool,
    is_math_expression,
    weather_tool,
    is_weather_question,
)

# Petit modèle HuggingFace pour les réponses "générales" (small talk, sans RAG)
chat_llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)


def small_talk_answer(question: str) -> str:
    """
    Réponse générale (salutations, questions non juridiques, etc.)
    sans passer par les textes de loi.
    """
    prompt = (
        "Tu es un assistant conversationnel poli et concis. "
        "Réponds en français, de manière simple.\n\n"
        f"Question : {question}\n\n"
        "Réponse :"
    )
    out = chat_llm(prompt, max_new_tokens=120)[0]["generated_text"]
    return out


def route_and_answer(question: str, use_rag: bool = True):
    """
    Routeur principal :

    - si expression mathématique → calculatrice
    - si question météo → outil météo
    - sinon :
        - si use_rag = True : RAG juridique (Code du travail, Code civil, PDF)
        - si use_rag = False : réponse générale (small talk HuggingFace)

    Retourne : (answer, docs)
      - docs = [] pour calculatrice / météo / small talk
      - docs = liste de Documents pour le RAG juridique
    """

    q_strip = question.strip()

    # 1. Calculatrice
    if is_math_expression(q_strip):
        answer = calculator_tool(q_strip)
        return answer, []

    # 2. Météo
    if is_weather_question(q_strip):
        answer = weather_tool(q_strip)
        return answer, []

    # 3. Juridique + RAG activé
    if use_rag:
        answer, docs = answer_with_rag(q_strip)
        return answer, docs

    # 4. Small talk / réponse générale sans RAG
    answer = small_talk_answer(q_strip)
    return answer, []
