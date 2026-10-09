"""
Tests for the rule-based sentiment classifier.
Run with: pytest tests/test_sentiment.py
"""

import pytest

from src.sentiment import classify_score


@pytest.mark.parametrize("score,expected", [
    (5, "Positive"),
    (4, "Positive"),
    (3, "Neutral"),
    (2, "Negative"),
    (1, "Negative"),
])
def test_classify_score_mapping(score, expected):
    assert classify_score(score) == expected


def test_classify_score_handles_none():
    # Missing/unknown scores should not crash; they default to Neutral.
    assert classify_score(None) == "Neutral"
