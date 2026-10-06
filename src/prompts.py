"""
prompts.py
----------
Prompt templates for the RAG chain.

The system prompt forces the model to stay grounded in the retrieved reviews
and to admit when it doesn't have enough information.
"""

from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "You are a customer-review analysis assistant. "
    "Answer ONLY using the reviews provided in the context. "
    "If the context does not contain the answer, say "
    "'Not enough information in the reviews.' Be concise and specific."
)

# The {context} placeholder is filled with retrieved reviews;
# {question} is the user's question.
USER_TEMPLATE = (
    "Reviews:\n{context}\n\n"
    "Question: {question}\n\n"
    "Respond with:\n"
    "1) A direct answer\n"
    "2) Up to 5 key themes\n"
    "3) Overall sentiment (positive / mixed / negative)"
)


def build_prompt() -> ChatPromptTemplate:
    """Return a ChatPromptTemplate combining the system and user messages."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_TEMPLATE),
        ]
    )

# TODO (Milestone 6): Experiment with the templates above. Try asking the model
# to include a short count of positive vs negative reviews, and observe how the
# wording changes grounding quality.
