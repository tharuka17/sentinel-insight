"""
Text agent — passes text through to the RAG pipeline.
Optionally runs a cheap zero-shot pre-screen to skip the LLM for clearly safe content.
"""

from loguru import logger

# Categories for zero-shot pre-screen
VIOLATION_LABELS = [
    "hate speech",
    "spam or scam",
    "adult content",
    "violence",
    "misinformation",
    "harassment",
    "safe content",
]


async def analyse_text(state: dict) -> dict:
    text = state.get("text", "")
    if not text:
        return {**state, "content_summary": ""}

    # Truncate very long inputs to first 2000 chars for efficiency
    summary = text[:2000]
    logger.debug(f"Text agent: {len(summary)} chars forwarded.")
    return {**state, "content_summary": summary}
