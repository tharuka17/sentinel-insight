"""
Run once to ingest policy documents into the pgvector store.

Usage:
    python scripts/ingest_policies.py
"""
import sys
import asyncio
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.config import settings


async def ingest():
    logger.info("Loading embedding model...")
    embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
    Settings.embed_model = embed_model

    logger.info("Connecting to pgvector...")
    vector_store = PGVectorStore.from_params(
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        table_name="policy_embeddings",
        embed_dim=384,
    )

    logger.info("Reading policy documents...")
    documents = SimpleDirectoryReader("data/policies").load_data()
    logger.info(f"Loaded {len(documents)} document chunks.")

    logger.info("Building index...")
    VectorStoreIndex.from_documents(documents, vector_store=vector_store)
    logger.info("Policy ingestion complete.")


if __name__ == "__main__":
    asyncio.run(ingest())
