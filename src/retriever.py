"""
retriever.py
------------
Builds a LangChain retriever over the pgvector store so we can fetch the
top-k reviews most relevant to a user's question.
"""

from langchain_core.vectorstores import VectorStoreRetriever

from src.config import load_config
from src.db import get_vector_store


def build_retriever() -> VectorStoreRetriever:
    """Return a retriever that fetches the top-k similar reviews."""
    cfg = load_config()
    store = get_vector_store()
    # as_retriever wraps the vector store with a standard retrieve interface.
    return store.as_retriever(search_kwargs={"k": cfg.top_k})
