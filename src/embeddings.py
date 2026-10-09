"""
embeddings.py
-------------
Builds the embedding model that converts review text into vectors.

We use a local, free sentence-transformers model via LangChain's
HuggingFaceEmbeddings wrapper. No API cost, runs on CPU.
"""

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import load_config


def build_embeddings() -> HuggingFaceEmbeddings:
    """Return a LangChain embeddings object using the configured model."""
    cfg = load_config()
    # HuggingFaceEmbeddings downloads the model on first use and caches it.
    return HuggingFaceEmbeddings(model_name=cfg.embedding_model)
