"""
db.py
-----
PostgreSQL connection helpers and the LangChain PGVector vector store.

Responsibilities:
- Provide a raw psycopg connection for inserting raw review rows.
- Provide a LangChain PGVector store for embeddings + similarity search.
"""

import re
from urllib.parse import urlsplit, urlunsplit

import psycopg
from langchain_postgres import PGVector

from src.config import load_config
from src.embeddings import build_embeddings

# Name of the LangChain collection (logical grouping of vectors).
COLLECTION_NAME = "customer_reviews"


def _parse_url(url: str) -> tuple[str, str | None]:
    """Split a DATABASE_URL into (clean_url_without_query, schema_or_None).

    Our .env uses '...?options=-csearch_path=kavitha' to pick the schema, but
    that query form is awkward for psycopg's URI parser. We extract the schema
    and return a clean URL plus the schema name to apply separately.
    """
    clean = url.replace("+psycopg", "")
    parts = urlsplit(clean)
    schema = None
    if parts.query:
        # Look for search_path=<schema> anywhere in the query/options string.
        match = re.search(r"search_path=([^&\s]+)", parts.query)
        if match:
            schema = match.group(1)
    # Rebuild the URL without the query string.
    clean_no_query = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return clean_no_query, schema


def get_connection() -> psycopg.Connection:
    """Open a raw psycopg connection to Postgres, using the configured schema."""
    cfg = load_config()
    clean_url, schema = _parse_url(cfg.database_url)
    # Include 'public' so the pgvector 'vector' type (installed there) resolves.
    options = f"-c search_path={schema},public" if schema else None
    return psycopg.connect(clean_url, options=options)


def get_vector_store() -> PGVector:
    """Return a LangChain PGVector store backed by Postgres/pgvector.

    This object is what the retriever and ingest modules use to add and
    search review embeddings. It uses the 'kavitha' schema via the search_path.

    """
    cfg = load_config()
    embeddings = build_embeddings()
    clean_url, schema = _parse_url(cfg.database_url)
    # SQLAlchemy/LangChain needs the explicit psycopg driver in the scheme.
    sa_url = clean_url.replace("postgresql://", "postgresql+psycopg://", 1)
    # Re-attach the schema as a libpq option so PGVector's tables live in it.
    # 'public' is included so the pgvector 'vector' type resolves.
    if schema:
        sa_url += f"?options=-csearch_path%3D{schema},public"
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=sa_url,
        use_jsonb=True,
    )


def ping() -> bool:
    """Return True if the database is reachable, False otherwise."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return cur.fetchone()[0] == 1
    except Exception:
        return False
