"""
Tests for prompt building (no DB or API needed).
Run with: uv run pytest tests/test_prompts.py
"""

from src.prompts import build_prompt


def test_prompt_contains_placeholders():
    prompt = build_prompt()
    # Rendering the template should require both variables.
    rendered = prompt.format(context="- Good product", question="What is good?")
    assert "Good product" in rendered
    assert "What is good?" in rendered


# TODO (Milestone 6): add a test asserting the system message tells the model to
# say "Not enough information" when the context is empty.
