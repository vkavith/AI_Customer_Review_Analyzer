"""
config.py
---------
Loads environment variables and exposes app configuration.

Why this exists: secrets (API keys) and settings should live in a `.env` file,
never hard-coded in source. This module is the single place that reads them.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from the local .env file into the environment.
load_dotenv()


@dataclass
class Config:
    active_provider: str
    groq_api_key: str | None
    groq_model: str
    openai_api_key: str | None
    openai_model: str
    database_url: str
    embedding_model: str
    top_k: int


def load_config() -> Config:
    """Read settings from the environment and return a Config object."""
    return Config(
        active_provider=os.getenv("ACTIVE_PROVIDER", "groq"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://localhost:5432/review_analyzer",
        ),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        top_k=int(os.getenv("TOP_K", "4")),
    )


def validate_config(cfg: Config) -> None:
    """Raise a clear error if required settings for the active provider are missing."""
    if cfg.active_provider == "groq" and not cfg.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    if cfg.active_provider == "openai" and not cfg.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")
