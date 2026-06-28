"""
RAG agent — retrieves the most relevant policy chunks for a given content summary.
Uses LlamaIndex + pgvector.
"""

from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from loguru import logger

from app.core.config import settings

_index: VectorStoreIndex | None = None


def _get_index() -> VectorStoreIndex:
    global _index
    if _index is None:
        embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        Settings.embed_model = embed_model

        vector_store = PGVectorStore.from_params(
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            table_name="policy_embeddings",
            embed_dim=384,
        )
        _index = VectorStoreIndex.from_vector_store(vector_store)
        logger.info("Policy index loaded from pgvector.")
    return _index


async def retrieve_policy(state: dict) -> dict:
    """Retrieve top-3 policy chunks relevant to the content summary."""
    summary = state.get("content_summary", "") or state.get("text", "") or ""
    if not summary:
        return {**state, "policy_chunks": []}

    try:
        index = _get_index()
        retriever = index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(summary)
        chunks = [
            {
                "rule_id": node.metadata.get("rule_id", f"rule_{i}"),
                "text": node.text,
                "score": round(node.score or 0.0, 4),
            }
            for i, node in enumerate(nodes)
        ]
        logger.debug(f"Retrieved {len(chunks)} policy chunks.")
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}. Continuing without policy context.")
        chunks = []

    return {**state, "policy_chunks": chunks}
