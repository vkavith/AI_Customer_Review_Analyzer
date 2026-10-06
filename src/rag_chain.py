"""
rag_chain.py
------------
Assembles the full Retrieval-Augmented Generation chain using LangChain.

Flow: question -> retriever -> format reviews into context -> prompt -> LLM -> text
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.llm_client import build_llm
from src.prompts import build_prompt
from src.retriever import build_retriever


def format_docs(docs) -> str:
    """Turn retrieved Documents into a single context string (one per line)."""
    return "\n".join(f"- {d.page_content}" for d in docs)


def build_rag_chain():
    """Wire retriever + prompt + llm into one runnable chain.

    The chain takes a question string and returns the model's answer text.
    """
    retriever = build_retriever()
    prompt = build_prompt()
    llm = build_llm()

    # LCEL (LangChain Expression Language) pipes components with '|'.
    # 'context' is produced by retrieving docs and formatting them;
    # 'question' passes straight through.
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def answer_question(question: str) -> str:
    """Build the chain and invoke it safely, returning the answer text."""
    try:
        chain = build_rag_chain()
        return chain.invoke(question)
    except Exception as e:
        return f"Sorry, the analyzer could not answer right now. ({e})"
