"""Deterministic intent routing for the industrial intelligence assistant."""

def route_question(question):
    if not isinstance(question, str) or not question.strip():
        return "invalid"
    q = question.casefold()
    if any(x in q for x in ("what if", "simulate", "simulation")):
        return "scenario"
    if any(x in q for x in ("last ", "past ", "history", "historical", "trend", "changed", "over the", "this week", "this month")):
        return "historical"
    if any(x in q for x in ("why", "cause", "reason", "what could be causing")):
        return "diagnostic"
    if "anomal" in q and "energy" in q:
        return "energy_anomaly"
    if any(x in q for x in ("equipment", "maintenance")):
        return "equipment"
    if any(x in q for x in ("safety", "incident")):
        return "safety"
    if "traffic" in q or "congestion" in q or "parking" in q:
        return "traffic"
    if any(x in q for x in ("aqi", "air quality", "pollution", "air-quality")):
        return "air_quality"
    if "waste" in q or "bin" in q:
        return "waste"
    if "water" in q:
        return "water"
    if any(x in q for x in ("energy", "power", "electricity")):
        if any(x in q for x in ("highest", "lowest", "most", "least", "compare", "which facility")):
            return "energy"
        return "energy"
    if any(x in q for x in ("what should", "recommend", "inspect", "prioritize", "action")):
        return "action"
    if any(x in q for x in ("today", "current", "currently", "now", "status", "biggest problems", "concerns")):
        return "current_status"
    if any(x in q for x in ("highest", "lowest", "most", "least", "compare", "comparison")):
        return "comparison"
    if any(x in q for x in ("what should", "recommend", "inspect", "prioritize", "action")):
        return "action"
    if "industrial intelligence system" in q:
        return "general"
    return "unknown"
