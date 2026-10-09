"""
Tests for ingest.load_csv (Amazon Fine Food Reviews format).

These test the parts you can verify WITHOUT a database connection:
validation, empty-text removal, deduplication, and sentiment labeling.
Run with: pytest tests/test_ingest.py
"""

import pytest

from src.ingest import load_csv


def test_load_valid_csv_returns_rows(tmp_path):
    # Arrange: a small valid CSV in the Amazon format (Id, Score, Text required)
    csv = tmp_path / "reviews.csv"
    csv.write_text(
        "Id,Score,Text\n"
        "1,5,Great product\n"
        "2,1,Terrible shipping\n"
    )
    # Act
    df = load_csv(str(csv))
    # Assert
    assert len(df) == 2
    assert "Text" in df.columns
    # load_csv derives a sentiment column from Score
    assert "sentiment" in df.columns


def test_load_csv_missing_column_raises(tmp_path):
    # Missing the required 'Text' (and 'Score') columns should raise.
    csv = tmp_path / "bad.csv"
    csv.write_text("Id,comment\n1,no required column here\n")
    with pytest.raises(ValueError):
        load_csv(str(csv))


def test_load_csv_drops_empty_reviews(tmp_path):
    # Rows with empty or whitespace-only Text must be dropped.
    csv = tmp_path / "reviews.csv"
    csv.write_text(
        'Id,Score,Text\n'
        '1,5,"Good"\n'
        '2,3,""\n'
        '3,4,"   "\n'
    )
    df = load_csv(str(csv))
    assert len(df) == 1
    assert df.iloc[0]["Text"] == "Good"


def test_load_csv_removes_duplicate_reviews(tmp_path):
    # Same user + text + time posted under different ProductIds = duplicate.
    csv = tmp_path / "reviews.csv"
    csv.write_text(
        "Id,ProductId,UserId,ProfileName,Time,Score,Text\n"
        "1,P1,U1,Alice,1000,5,Love it\n"
        "2,P2,U1,Alice,1000,5,Love it\n"  # duplicate submission
        "3,P3,U2,Bob,2000,2,Hate it\n"
    )
    df = load_csv(str(csv))
    # Only the first of the duplicate pair + the unique Bob review remain.
    assert len(df) == 2
    assert set(df["Text"]) == {"Love it", "Hate it"}


def test_load_csv_assigns_sentiment(tmp_path):
    csv = tmp_path / "reviews.csv"
    csv.write_text(
        "Id,Score,Text\n"
        "1,5,Excellent\n"
        "2,3,Okay\n"
        "3,1,Awful\n"
    )
    df = load_csv(str(csv)).set_index("Id")
    assert df.loc[1, "sentiment"] == "Positive"
    assert df.loc[2, "sentiment"] == "Neutral"
    assert df.loc[3, "sentiment"] == "Negative"


def test_load_csv_respects_limit(tmp_path):
    csv = tmp_path / "reviews.csv"
    rows = "\n".join(f"{i},5,Review {i}" for i in range(1, 11))
    csv.write_text("Id,Score,Text\n" + rows + "\n")
    df = load_csv(str(csv), limit=3)
    assert len(df) == 3
