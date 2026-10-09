"""Tests for prompt construction and numeric grounding of LLM explanations."""

from ai.assistant.guardrails import validate_explanation
from ai.assistant.prompts import build_explanation_prompt


def test_guardrails_accept_explanation_without_unsupported_numbers():
    trusted_context = '{"actual": 120, "expected": 100, "deviation": "20%"}'

    assert validate_explanation(
        "The reading is above its expected baseline.",
        trusted_context,
    ) == "The reading is above its expected baseline."
    assert validate_explanation("The value is 120.", trusted_context) == "The value is 120."


def test_guardrails_reject_new_numeric_claims_and_empty_text():
    trusted_context = '{"actual": 120, "expected": 100}'

    assert validate_explanation("The value is 135.", trusted_context) is None
    assert validate_explanation("   ", trusted_context) is None
    assert validate_explanation(None, trusted_context) is None


def test_explanation_prompt_contains_question_and_trusted_evidence():
    prompt = build_explanation_prompt(
        "Why is energy high?",
        {"actual": 120, "expected": 100},
    )

    assert "Why is energy high?" in prompt
    assert '"actual": 120' in prompt
    assert "Do not invent data" in prompt
