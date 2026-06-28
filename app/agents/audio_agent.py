"""
Audio agent — transcribes audio using OpenAI Whisper, then passes transcript to the verdict pipeline.
"""

import tempfile
import os
import whisper
from loguru import logger

_model = None


def _load_whisper():
    global _model
    if _model is None:
        logger.info("Loading Whisper model...")
        _model = whisper.load_model(
            "base"
        )  # swap to "small" / "medium" for better accuracy
        logger.info("Whisper loaded.")


async def analyse_audio(state: dict) -> dict:
    file_bytes = state.get("file_bytes")
    if not file_bytes:
        return {**state, "content_summary": "No audio data provided."}

    _load_whisper()

    # Whisper needs a file path
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        result = _model.transcribe(tmp_path, fp16=False)
        transcript = result["text"].strip()
    finally:
        os.unlink(tmp_path)

    logger.debug(f"Audio transcript ({len(transcript)} chars)")
    return {**state, "content_summary": f"[Audio transcript] {transcript}"}
