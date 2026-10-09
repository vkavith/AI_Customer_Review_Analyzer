"""
sentiment.py
------------
Rule-based sentiment classification derived from the Amazon review Score.

For the Amazon Fine Food Reviews dataset, each review has a Score (1-5 stars).
We map that star rating to a sentiment category:
    Score >= 4  -> "Positive"
    Score == 3  -> "Neutral"
    Score <= 2  -> "Negative"

This is a simple, transparent baseline (no training required). Later you can
optionally replace/augment it with an LLM-based classifier.
"""


def classify_score(score: int) -> str:
    """Return a sentiment label for a 1-5 star score."""
    if score is None:
        return "Neutral"
    if score >= 4:
        return "Positive"
    if score == 3:
        return "Neutral"
    return "Negative"
