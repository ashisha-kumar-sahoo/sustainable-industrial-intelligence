"""Prompt construction for the optional local language-model explanation."""

import json


def build_explanation_prompt(question: str, trusted_context: dict) -> str:
    """Build a constrained prompt from deterministic decision-layer evidence."""
    serialized_context = json.dumps(
        trusted_context,
        default=str,
        ensure_ascii=False,
    )
    return (
        "Write one concise natural-language explanation using only the supplied JSON. "
        "Do not invent data, change values, create facilities, or claim unsupported "
        "anomalies or predictions. Do not include digits or numerical measurements "
        "in the explanation; exact figures are already in the structured evidence. "
        "If information is unavailable, say so. Return explanation only.\n"
        f"QUESTION: {question}\nTRUSTED JSON: {serialized_context}"
    )
