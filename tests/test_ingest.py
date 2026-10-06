"""
Tests for ingest.load_csv.

These test the parts you can verify WITHOUT a database connection.
Run with: uv run pytest tests/test_ingest.py
"""

import pandas as pd
import pytest

from src.ingest import load_csv


def test_load_valid_csv_returns_rows(tmp_path):
    # Arrange: write a small valid CSV
    csv = tmp_path / "reviews.csv"
    csv.write_text("review_text\nGreat product\nTerrible shipping\n")
    # Act
    df = load_csv(str(csv))
    # Assert
    assert len(df) == 2
    assert "review_text" in df.columns


def test_load_csv_missing_column_raises(tmp_path):
    csv = tmp_path / "bad.csv"
    csv.write_text("comment\nno required column here\n")
    with pytest.raises(ValueError):
        load_csv(str(csv))


def test_load_csv_drops_empty_reviews(tmp_path):
    csv = tmp_path / "reviews.csv"
    csv.write_text('review_text\n"Good"\n""\n"   "\n')
    df = load_csv(str(csv))
    # TODO (Milestone 2): confirm the empty/whitespace rows were dropped.
    # Replace the line below with a real assertion once you understand it.
    assert len(df) == 1
