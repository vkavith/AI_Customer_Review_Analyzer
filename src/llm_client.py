"""
llm_client.py
-------------
Builds the chat LLM used for generation (OpenAI).
"""

from langchain_openai import ChatOpenAI

from src.config import load_config


def build_llm():
    """Return a LangChain OpenAI chat model."""
    cfg = load_config()
    # temperature=0 keeps answers focused and less "creative"
    return ChatOpenAI(
        model=cfg.openai_model,
        api_key=cfg.openai_api_key,
        temperature=0,
    )
