# src/agents/tools.py

import re
from datetime import datetime
import random


def is_math_expression(text: str) -> bool:
    """
    Détecte si le texte ressemble à une expression mathématique simple.
    Ex : "2+3*5", "10 / 4", "3.5 * 2"
    """
    pattern = r"^[0-9\.\,\s\+\-\*\/\(\)]+$"
    return re.match(pattern, text.strip()) is not None


def calculator_tool(expr: str) -> str:
    """
    Calculatrice très simple, sécurisée : gère + - * / et parenthèses.
    """
    try:
        # On remplace la virgule par un point pour les décimales
        expr_clean = expr.replace(",", ".")
        # Limiter les caractères autorisés
        if not is_math_expression(expr_clean):
            return "Je ne peux calculer que des expressions numériques simples (avec +, -, *, /)."
        result = eval(expr_clean, {"__builtins__": {}})
        return f"Résultat du calcul `{expr}` : **{result}**"
    except Exception:
        return "Je n'ai pas réussi à calculer cette expression. Vérifie la syntaxe."


def weather_tool(question: str) -> str:
    """
    Outil météo simulé.
    Pour le DU, il suffit d'expliquer que c'est une API fictive.
    """
    villes = ["Paris", "Lyon", "Marseille", "Toulouse", "Lille"]
    today = datetime.now().strftime("%d/%m/%Y")

    # Cherche une ville dans la question
    ville_trouvee = None
    for v in villes:
        if v.lower() in question.lower():
            ville_trouvee = v
            break

    ville = ville_trouvee or "Paris"
    temp = random.randint(10, 28)
    cond = random.choice(["ensoleillé", "nuageux", "pluvieux", "partiellement couvert"])

    return (
        f"🌤️ Météo simulée pour **{ville}** le {today} :\n\n"
        f"- Température : **{temp}°C**\n"
        f"- Conditions : **{cond}**\n\n"
        "_(Données issues d'une API fictive dans le cadre du projet.)_"
    )


def is_weather_question(text: str) -> bool:
    """
    Détecte si la question parle de météo.
    """
    keywords = ["météo", "meteo", "temps", "fait-il", "temperature", "température"]
    text_low = text.lower()
    return any(k in text_low for k in keywords)
