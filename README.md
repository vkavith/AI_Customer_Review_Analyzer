# AI Customer Review Analyzer

A Retrieval-Augmented Generation (RAG) application that analyzes customer reviews
using **LangChain**, an open-source LLM (via **Groq**), and **PostgreSQL + pgvector**.

Ask natural-language questions about your reviews (e.g. *"What do customers
complain about most?"*) and get grounded, evidence-backed answers.

## Tech Stack
- **LangChain** — orchestrates the RAG pipeline (loaders, splitters, retriever, chains)
- **Groq API** — serves open-source Llama 3.x models (active provider)
- **OpenAI** — optional fallback (kept, commented in config)
- **PostgreSQL + pgvector** — vector store for review embeddings
- **sentence-transformers** — local embeddings (all-MiniLM-L6-v2)
- **Streamlit** — UI
- **uv** — dependency management

## Prerequisites
1. Python 3.10+
2. PostgreSQL with the `pgvector` extension
3. A free Groq API key: https://console.groq.com/
4. [`uv`](https://docs.astral.sh/uv/) installed

## Setup
```bash
# 1. Install dependencies
uv sync

# 2. Create the database and enable pgvector
createdb review_analyzer
psql -d review_analyzer -f sql/schema.sql

# 3. Configure secrets
cp .env.example .env
# then edit .env and add your GROQ_API_KEY

# 4. Load sample data (after you complete ingest.py)
uv run python -m src.ingest data/sample_reviews.csv

# 5. Run the app
uv run streamlit run app.py
```

## Project Structure
```
app.py            # Streamlit UI (wires components together)
src/
  config.py       # Loads env vars, selects active LLM provider
  db.py           # Postgres connection + pgvector helpers
  ingest.py       # CSV -> validated rows -> embeddings -> DB
  embeddings.py   # Builds the embedding model
  retriever.py    # LangChain retriever over pgvector
  prompts.py      # System + user prompt templates
  llm_client.py   # LangChain LLM (Groq active, OpenAI fallback)
  rag_chain.py    # Assembles the RAG chain
sql/schema.sql    # Database schema
data/             # Sample reviews CSV
tests/            # pytest tests
```

## Status
This is a capstone scaffold. Several core functions contain `TODO`s that the
developer must complete as part of the learning milestones in
`implementation_plan.md`.

## Limitations
- Only as good as the uploaded reviews; not a statistical survey.
- LLMs can hallucinate — answers are grounded in retrieved reviews, but verify.
- Do not treat output as legal, medical, or financial advice.

## License
MIT
