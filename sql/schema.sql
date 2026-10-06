-- Database schema for the AI Customer Review Analyzer
-- Dataset: Amazon Fine Food Reviews (data/Reviews.csv)
-- Run with: psql -d postgres -f sql/schema.sql

-- 1. Create the application schema and use it for the rest of this script.
CREATE SCHEMA IF NOT EXISTS kavitha;
SET search_path TO kavitha;

-- 2. Enable the pgvector extension (required for RAG vector similarity search).
--    Extensions live at the database level; this is safe to run once.
CREATE EXTENSION IF NOT EXISTS vector;

-- 3. Reviews table - columns mirror Reviews.csv, plus a derived 'sentiment'.
--    Score -> sentiment mapping (done at ingest time):
--      Score >= 4  -> 'Positive'
--      Score == 3  -> 'Neutral'
--      Score <= 2  -> 'Negative'
CREATE TABLE IF NOT EXISTS reviews (
    id                      INTEGER PRIMARY KEY,   -- maps to CSV "Id"
    product_id              TEXT,                  -- "ProductId"
    user_id                 TEXT,                  -- "UserId"
    profile_name            TEXT,                  -- "ProfileName"
    helpfulness_numerator   INTEGER,               -- "HelpfulnessNumerator"
    helpfulness_denominator INTEGER,               -- "HelpfulnessDenominator"
    score                   INTEGER,               -- "Score" (1..5)
    review_time             BIGINT,                -- "Time" (unix epoch)
    summary                 TEXT,                  -- "Summary"
    review_text             TEXT NOT NULL,         -- "Text"
    sentiment               TEXT                   -- derived: Positive/Neutral/Negative
);

-- 4. Indexes to speed up common queries and the sentiment chart.
CREATE INDEX IF NOT EXISTS idx_reviews_product   ON reviews (product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_score     ON reviews (score);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews (sentiment);

-- Note: LangChain's PGVector stores embeddings in its own tables
-- (langchain_pg_collection / langchain_pg_embedding). They are created in the
-- 'kavitha' schema as long as the connection's search_path points there.
-- This 'reviews' table holds the raw + classified data for analysis and charts.
