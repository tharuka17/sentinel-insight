"""
Image agent — generates a text caption from an image using BLIP-2.
The caption feeds into the RAG + verdict pipeline.
"""

import io

import torch
from loguru import logger
from PIL import Image
from transformers import Blip2ForConditionalGeneration, Blip2Processor

_processor = None
_model = None


def _load_blip2():
    global _processor, _model
    if _processor is None:
        logger.info("Loading BLIP-2 model (first call — may take a moment)...")
        _processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        _model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-opt-2.7b",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(device)
        logger.info(f"BLIP-2 loaded on {device}.")


async def analyse_image(state: dict) -> dict:
    file_bytes = state.get("file_bytes")
    if not file_bytes:
        return {**state, "content_summary": "No image data provided."}

    _load_blip2()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    inputs = _processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        ids = _model.generate(**inputs, max_new_tokens=128)

    caption = _processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

    # Append any original text caption the user provided
    user_text = state.get("text", "")
    summary = f"[Image caption] {caption}"
    if user_text:
        summary += f"\n[User caption] {user_text}"

    logger.debug(f"Image caption: {caption}")
    return {**state, "content_summary": summary}
