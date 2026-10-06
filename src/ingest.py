"""
ingest.py
---------
Load the Amazon Fine Food Reviews dataset (data/Reviews.csv), classify each
review's sentiment from its Score, insert rows into Postgres, and (optionally)
index a sample into the vector store for RAG.

Run from the command line:
    # Insert rows into Postgres (use --limit while developing - the full file
    # has ~568k rows):
    uv run python -m src.ingest data/Reviews.csv --limit 2000

    # Also build the vector index for RAG (slower; embeds each review):
    uv run python -m src.ingest data/Reviews.csv --limit 2000 --index
"""

import argparse

import pandas as pd
from langchain_core.documents import Document

from src.db import get_connection, get_vector_store
from src.sentiment import classify_score

# Columns we rely on from Reviews.csv
REQUIRED_COLUMNS = {"Id", "Score", "Text"}


def load_csv(path: str, limit: int | None = None) -> pd.DataFrame:
    """Read Reviews.csv, validate columns, drop empty text, dedupe, add sentiment."""
    df = pd.read_csv(path, nrows=limit)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required column(s): {missing}")

    # Remove rows with empty review text (nothing to analyze).
    df = df.dropna(subset=["Text"])
    df = df[df["Text"].astype(str).str.strip() != ""]

    # --- Deduplication ---
    before = len(df)
    # 1) Drop exact duplicate review submissions. The Amazon dataset contains
    #    the same review posted under multiple ProductIds; a review is a true
    #    duplicate when the same user posted the same text at the same time.
    dedupe_keys = [c for c in ["UserId", "ProfileName", "Time", "Text"] if c in df.columns]
    if dedupe_keys:
        df = df.drop_duplicates(subset=dedupe_keys, keep="first")
    # 2) Safety net: never insert the same primary-key Id twice.
    df = df.drop_duplicates(subset=["Id"], keep="first")
    removed = before - len(df)
    if removed:
        print(f"Removed {removed} duplicate reviews.")

    # Derive the sentiment label from the star Score.
    df["sentiment"] = df["Score"].apply(classify_score)
    return df


def insert_raw_rows(df: pd.DataFrame) -> int:
    """Insert review rows into the Postgres 'reviews' table.

    Uses a parameterized executemany so user data is never string-formatted
    into SQL. Returns the number of rows inserted.
    """
    rows = [
        (
            int(r.Id),
            getattr(r, "ProductId", None),
            getattr(r, "UserId", None),
            getattr(r, "ProfileName", None),
            _safe_int(getattr(r, "HelpfulnessNumerator", None)),
            _safe_int(getattr(r, "HelpfulnessDenominator", None)),
            _safe_int(r.Score),
            _safe_int(getattr(r, "Time", None)),
            getattr(r, "Summary", None),
            str(r.Text),
            r.sentiment,
        )
        for r in df.itertuples(index=False)
    ]

    sql = """
        INSERT INTO reviews (
            id, product_id, user_id, profile_name,
            helpfulness_numerator, helpfulness_denominator,
            score, review_time, summary, review_text, sentiment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
        conn.commit()
    return len(rows)


def index_reviews(df: pd.DataFrame) -> int:
    """Add reviews to the LangChain vector store for RAG retrieval.

    Each review becomes a Document whose page_content is the text and whose
    metadata carries product_id, score, and sentiment (useful for filtering).
    """
    docs = [
        Document(
            page_content=str(r.Text),
            metadata={
                "id": int(r.Id),
                "product_id": getattr(r, "ProductId", None),
                "score": _safe_int(r.Score),
                "sentiment": r.sentiment,
            },
        )
        for r in df.itertuples(index=False)
    ]
    store = get_vector_store()
    store.add_documents(docs)
    return len(docs)


def _safe_int(value) -> int | None:
    """Convert a value to int, returning None if it can't be converted."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Amazon reviews into Postgres.")
    parser.add_argument("path", help="Path to Reviews.csv")
    parser.add_argument("--limit", type=int, default=None, help="Max rows to load")
    parser.add_argument("--index", action="store_true", help="Also build vector index")
    args = parser.parse_args()

    df = load_csv(args.path, limit=args.limit)
    print(f"Loaded {len(df)} valid reviews from {args.path}")

    inserted = insert_raw_rows(df)
    print(f"Inserted {inserted} rows into Postgres (duplicates skipped).")

    if args.index:
        count = index_reviews(df)
        print(f"Indexed {count} reviews into the vector store.")


if __name__ == "__main__":
    main()
