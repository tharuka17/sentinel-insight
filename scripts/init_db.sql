CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS policy_embeddings (
    id          SERIAL PRIMARY KEY,
    text        TEXT NOT NULL,
    metadata_   JSONB,
    embedding   vector(384)
);

CREATE INDEX IF NOT EXISTS policy_embeddings_hnsw
    ON policy_embeddings USING hnsw (embedding vector_cosine_ops);
