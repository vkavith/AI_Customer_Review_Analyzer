# AI Customer Review Analyzer

A **Retrieval-Augmented Generation (RAG)** application that analyzes the
**Amazon Fine Food Reviews** dataset. It classifies every review's sentiment
(**Positive / Neutral / Negative**), visualizes the breakdown, and lets you ask
natural-language questions (e.g. *"What do customers say about taste and
quality?"*) that are answered with evidence grounded in real reviews.

Built with **LangChain**, **OpenAI**, and **PostgreSQL + pgvector**.

---

## Features

1. **Sentiment Dashboard** — classifies reviews from their star score and shows
   an interactive pie chart of the Positive/Neutral/Negative distribution.
2. **Ask the Reviews (RAG)** — retrieves the most relevant reviews with vector
   similarity search and uses an LLM to produce a grounded answer.

---

## Tech Stack

| Layer | Tool | Role |
|-------|------|------|
| UI | **Streamlit** | Web dashboard |
| Orchestration | **LangChain** | Connects retrieval → prompt → LLM |
| LLM | **OpenAI** (`gpt-4o-mini`) | Generates answers |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Local, free text→vector |
| Database | **PostgreSQL + pgvector** | Stores reviews and vector embeddings |
| Data | **pandas** | Reads/cleans the CSV |
| Visualization | **plotly** | Sentiment pie chart |
| Config | **python-dotenv** | Loads secrets from `.env` |

---

## Dataset

[Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews)
(~568k reviews of food/grocery products). Place the file at `data/Reviews.csv`.

> **Note:** `data/Reviews.csv` (~287 MB) is **not** committed to git (it exceeds
> GitHub's 100 MB limit). Download it separately from the link above and place it
> at `data/Reviews.csv` before loading data.

**Sentiment mapping:** Score 4–5 → Positive · Score 3 → Neutral · Score 1–2 → Negative.

---

## Prerequisites

1. Python 3.10+
2. PostgreSQL (with the `pgvector` extension installed)
3. An OpenAI API key: https://platform.openai.com/

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv312
source .venv312/bin/activate        # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the schema + table and enable pgvector
#    (uses the 'postgres' database and a 'kavitha' schema)
psql -h localhost -U postgres -d postgres -f sql/schema.sql

# 4. Configure secrets
cp .env.example .env
# then edit .env (see Configuration below)
```

### Configuration (`.env`)

```properties
# Postgres (schema is selected via the search_path option)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres?options=-csearch_path=kavitha

# LLM provider
ACTIVE_PROVIDER=openai
OPENAI_API_KEY=sk-...your_key...
OPENAI_MODEL=gpt-4o-mini

# Local embedding model (free, no key required)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Retrieval: how many reviews to pull per question
TOP_K=4
```

---

## Loading Data

```bash
# Load + classify reviews into Postgres (start small while testing).
# Duplicates are removed automatically.
python -m src.ingest data/Reviews.csv --limit 2000

# Add --index to also embed reviews into pgvector (needed for the RAG Q&A).
python -m src.ingest data/Reviews.csv --limit 500 --index

# Load everything (no limit):
python -m src.ingest data/Reviews.csv
```

---

## Running the App

```bash
python -m streamlit run app.py
```

Then open http://localhost:8501.

- **Sentiment Overview** works once rows are loaded (step above).
- **Ask About the Reviews** works once reviews are indexed with `--index`.

---

## Example

**Question:** *"What do customers say about the taste and quality?"*

**Answer (grounded in retrieved reviews):**
> 1) Customers have mixed feelings — some find it lacking flavor or mushy, others
> describe it as fresh but just "alright."
> 2) Key themes: flavor, texture, freshness, brand comparison, price.
> 3) Overall sentiment: Mixed.

Ask an off-topic question (e.g. *"What's the weather?"*) and the model correctly
replies that there is **not enough information in the reviews** — it does not
hallucinate.

---

## Project Structure

```
app.py                # Streamlit UI (sentiment chart + RAG Q&A)
requirements.txt      # Dependencies
sql/schema.sql        # Creates kavitha schema + reviews table + indexes
data/
  Reviews.csv         # Amazon dataset (gitignored - download separately)
src/
  config.py           # Loads env vars, selects active LLM provider
  db.py               # Postgres connection + pgvector store (schema-aware)
  embeddings.py       # Local embedding model
  sentiment.py        # Star score -> Positive/Neutral/Negative
  ingest.py           # CSV -> dedupe -> classify -> insert (+ optional index)
  analytics.py        # Sentiment counts for the chart
  retriever.py        # Top-k vector similarity retriever
  prompts.py          # Grounded system + user prompt templates
  llm_client.py       # OpenAI chat model
  rag_chain.py        # Assembles the full RAG chain (LCEL)
tests/                # pytest tests (ingest, prompts)
```

---

## How It Works

**Ingestion:** `Reviews.csv` → validate & dedupe → classify sentiment → insert
into `kavitha.reviews` → (optional) embed text into pgvector.

**Query (RAG):** your question → embedded → **cosine similarity search** in
pgvector returns the top-k reviews → formatted into context → inserted into a
grounded prompt → sent to OpenAI → answer displayed.

---

## Testing

```bash
pytest
```

---

## Limitations

- Answers are only as good as the reviews; this is not a statistical survey.
- RAG answers see only the top-k retrieved reviews — use the **dashboard** for
  totals/counts, not the Q&A.
- LLMs can hallucinate; answers are grounded but should be verified.
- Dataset covers food/grocery products only.
- Do not treat output as legal, medical, or financial advice.

---

## License

MIT
