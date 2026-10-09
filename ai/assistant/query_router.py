"""Deterministic intent routing for the industrial intelligence assistant."""


def route_question(question: str) -> str:
    """Map a user's question to the domain-specific decision handler."""
    if not isinstance(question, str) or not question.strip():
        return "invalid"

    normalized_question = question.casefold()

    if any(term in normalized_question for term in ("what if", "simulate", "simulation")):
        return "scenario"

    historical_terms = (
        "last ",
        "past ",
        "history",
        "historical",
        "trend",
        "changed",
        "over the",
        "this week",
        "this month",
    )
    if any(term in normalized_question for term in historical_terms):
        return "historical"

    if any(
        term in normalized_question
        for term in ("why", "cause", "reason", "what could be causing")
    ):
        return "diagnostic"

    if "anomal" in normalized_question and "energy" in normalized_question:
        return "energy_anomaly"

    if any(term in normalized_question for term in ("equipment", "maintenance")):
        return "equipment"

    if any(term in normalized_question for term in ("safety", "incident")):
        return "safety"

    if any(
        term in normalized_question
        for term in ("traffic", "congestion", "parking")
    ):
        return "traffic"

    if any(
        term in normalized_question
        for term in ("aqi", "air quality", "pollution", "air-quality")
    ):
        return "air_quality"

    if "waste" in normalized_question or "bin" in normalized_question:
        return "waste"
    if "water" in normalized_question:
        return "water"

    if any(
        term in normalized_question
        for term in ("energy", "power", "electricity")
    ):
        return "energy"

    if any(
        term in normalized_question
        for term in ("what should", "recommend", "inspect", "prioritize", "action")
    ):
        return "action"

    if any(
        term in normalized_question
        for term in (
            "today",
            "current",
            "currently",
            "now",
            "status",
            "biggest problems",
            "concerns",
        )
    ):
        return "current_status"

    if any(
        term in normalized_question
        for term in ("highest", "lowest", "most", "least", "compare", "comparison")
    ):
        return "comparison"

    if "industrial intelligence system" in normalized_question:
        return "general"

    return "unknown"
