"""
analytics.py
------------
Query helpers for summarizing the classified reviews stored in Postgres.
Used by the Streamlit UI to draw the sentiment chart.
"""

import pandas as pd

from src.db import get_connection


def sentiment_counts() -> pd.DataFrame:
    """Return a DataFrame with columns [sentiment, count] from the DB."""
    sql = """
        SELECT sentiment, COUNT(*) AS count
        FROM reviews
        GROUP BY sentiment
        ORDER BY count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


def total_reviews() -> int:
    """Return the total number of reviews currently stored."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM reviews")
            return cur.fetchone()[0]


# Practice task (optional):
# Add a function sentiment_by_product(product_id) that returns sentiment counts
# filtered to a single ProductId, so users can analyze one product at a time.
