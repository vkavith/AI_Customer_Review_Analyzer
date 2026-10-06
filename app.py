"""
app.py
------
Streamlit UI for the AI Customer Review Analyzer.

Two features:
  1. Sentiment dashboard - classify reviews (Positive/Neutral/Negative) and chart them.
  2. Ask questions about the reviews using RAG (LangChain + Groq).

This file should ONLY wire components together - keep DB/LLM logic in src/.
"""

import plotly.express as px
import streamlit as st

from src.analytics import sentiment_counts, total_reviews
from src.rag_chain import answer_question

st.set_page_config(page_title="AI Customer Review Analyzer", page_icon="📝", layout="wide")

st.title("📝 AI Customer Review Analyzer")
st.caption("Classify customer sentiment and ask grounded questions (LangChain + RAG).")

# --- Sidebar: data ingestion hint ---
with st.sidebar:
    st.header("Data")
    st.write(
        "Load the Amazon reviews first, e.g.:\n\n"
        "`uv run python -m src.ingest data/Reviews.csv --limit 2000`\n\n"
        "Add `--index` to also build the RAG vector index."
    )

# --- Section 1: Sentiment dashboard ---
st.subheader("Sentiment Overview")

# Fixed colors so each category always looks the same.
COLORS = {"Positive": "#2ecc71", "Neutral": "#f1c40f", "Negative": "#e74c3c"}

try:
    counts = sentiment_counts()
    if counts.empty:
        st.info("No reviews found yet. Run the ingest command shown in the sidebar.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("Total reviews", f"{total_reviews():,}")
            st.dataframe(counts, hide_index=True, use_container_width=True)
        with col2:
            fig = px.pie(
                counts,
                names="sentiment",
                values="count",
                color="sentiment",
                color_discrete_map=COLORS,
                title="Review Sentiment Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)
except Exception as e:  # DB might be offline / not yet seeded
    st.warning(f"Could not load sentiment data: {e}")

st.divider()

# --- Section 2: Ask a question (RAG) ---
st.subheader("Ask About the Reviews")
question = st.text_input("Your question", placeholder="What do customers complain about most?")

if st.button("Analyze"):
    # Basic input validation before doing expensive work.
    if not question or len(question.strip()) < 5:
        st.warning("Please enter a question with at least 5 characters.")
    else:
        with st.spinner("Analyzing reviews..."):
            try:
                answer = answer_question(question)
                st.markdown(answer)
            except Exception as e:
                st.error(f"Sorry, the analyzer is unavailable right now. ({e})")
