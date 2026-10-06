"""
llm_client.py
-------------
Builds the chat LLM used for generation.

OpenAI is the ACTIVE provider. Groq is kept as an alternative.
"""

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from src.config import load_config


def build_llm():
    """Return a LangChain chat model based on the active provider."""
    cfg = load_config()

    if cfg.active_provider == "openai":
        # temperature=0 keeps answers focused and less "creative"
        return ChatOpenAI(
            model=cfg.openai_model,
            api_key=cfg.openai_api_key,
            temperature=0,
        )

    if cfg.active_provider == "groq":
        return ChatGroq(
            model=cfg.groq_model,
            api_key=cfg.groq_api_key,
            temperature=0,
        )

    raise ValueError(f"Unknown provider: {cfg.active_provider}")


# Practice task (Milestone 5):
# Write a short script that builds the LLM and calls
# llm.invoke("Say hello in one sentence.") then prints the .content.
# Then wrap it in try/except and force an error (e.g. bad key) to see your
# error handling work.
