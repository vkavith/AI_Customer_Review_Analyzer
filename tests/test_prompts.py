"""
Tests for prompt building (no DB or API needed).
Run with: pytest tests/test_prompts.py
"""

from src.prompts import build_prompt


def test_prompt_contains_placeholders():
    prompt = build_prompt()
    # Rendering the template should include both variables.
    rendered = prompt.format(context="- Good product", question="What is good?")
    assert "Good product" in rendered
    assert "What is good?" in rendered


def test_prompt_instructs_grounding():
    # The system message should tell the model to avoid hallucinating and
    # admit when the reviews don't contain the answer.
    prompt = build_prompt()
    rendered = prompt.format(context="", question="anything").lower()
    assert "not enough information" in rendered
