"""Small output checks for optional LLM explanations.

The database/rule-based decision remains authoritative. These checks reject an
LLM explanation if it introduces a numerical token that was not present in the
trusted evidence supplied to the model.
"""

import re

NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?%?")



    
from decimal import Decimal, InvalidOperation


def contains_only_grounded_numbers(
    text: str,
    trusted_context: str,
) -> bool:
    """Check that every generated number is grounded in trusted context."""

    trusted_numbers = {
        _normalize_number(number)
        for number in NUMBER_PATTERN.findall(trusted_context)
    }

    generated_numbers = NUMBER_PATTERN.findall(text)

    for number in generated_numbers:
        normalized_number = _normalize_number(number)

        if normalized_number not in trusted_numbers:
            return False

    return True


def _normalize_number(number: str) -> str:
    """Normalize equivalent numeric representations such as 20 and 20.0."""
    numeric_text = number.rstrip("%")

    try:
        value = Decimal(numeric_text)
    except InvalidOperation:
        return numeric_text

    return format(value.normalize(), "f")



def validate_explanation(text: str | None, trusted_context: str) -> str | None:
    """Return a safe explanation or None when it is empty or ungrounded."""
    if not isinstance(text, str):
        return None

    explanation = text.strip()
    if not explanation:
        return None

    if not contains_only_grounded_numbers(explanation, trusted_context):
        return None

    return explanation
