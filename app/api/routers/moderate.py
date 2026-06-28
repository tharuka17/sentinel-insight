"""
POST /api/v1/moderate — accepts text, image, or audio and returns a moderation verdict.
"""

import magic
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.agents.orchestrator import run_pipeline
from app.core.celery_app import celery_app

router = APIRouter()


class ModerationResult(BaseModel):
    verdict: str  # "approved" | "flagged" | "escalated"
    category: Optional[str]  # e.g. "hate_speech"
    confidence: float  # 0.0 – 1.0
    policy_rule_ids: list[str]  # cited policy chunks
    reasoning: str  # LLM explanation
    modality: str  # "text" | "image" | "audio"
    job_id: Optional[str] = None  # async job id if queued


@router.post("/moderate", response_model=ModerationResult)
async def moderate_content(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    async_mode: bool = Form(False),
):
    """
    Submit content for moderation. Accepts:
    - text (Form field)
    - image/audio file (multipart upload)
    Combine both for richest context (e.g. an image + its caption).
    """
    if not text and not file:
        raise HTTPException(status_code=422, detail="Provide text or a file.")

    payload = {"text": text}

    if file:
        raw = await file.read()
        mime = magic.from_buffer(raw, mime=True)
        payload["file_bytes"] = raw
        payload["mime_type"] = mime

    if async_mode:
        task = celery_app.send_task("tasks.moderate", kwargs={"payload": payload})
        return ModerationResult(
            verdict="queued",
            category=None,
            confidence=0.0,
            policy_rule_ids=[],
            reasoning="Task queued for async processing.",
            modality="unknown",
            job_id=task.id,
        )

    result = await run_pipeline(payload)
    return result
