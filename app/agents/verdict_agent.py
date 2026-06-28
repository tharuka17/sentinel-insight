"""
Verdict agent — calls the LLM with content + policy context and extracts a structured decision.
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

from app.core.config import settings

SYSTEM_PROMPT = """You are a content moderation AI assistant.
You will be given:
1. A summary of the content to evaluate.
2. Relevant policy excerpts (each with a rule_id).

Your job is to decide if the content violates any policy.

Respond ONLY with a JSON object (no markdown, no extra text):
{
  "verdict": "approved" | "flagged" | "escalated",
  "category": "<violation category or null>",
  "confidence": <float 0.0-1.0>,
  "policy_rule_ids": ["<cited rule_id>", ...],
  "reasoning": "<one or two sentences explaining the decision>"
}

Rules:
- "approved" = no policy violation found
- "flagged" = clear violation, automated action
- "escalated" = ambiguous — needs human review
- Only cite rule_ids that actually appear in the policy excerpts provided.
- confidence reflects your certainty in the verdict."""


async def generate_verdict(state: dict) -> dict:
    content = state.get("content_summary") or state.get("text") or ""
    chunks = state.get("policy_chunks") or []

    policy_context = (
        "\n\n".join(f"[{c['rule_id']}] {c['text']}" for c in chunks)
        or "No specific policy rules retrieved."
    )

    human_msg = f"CONTENT:\n{content}\n\nPOLICY EXCERPTS:\n{policy_context}"

    llm = ChatOpenAI(
        base_url=settings.VLLM_BASE_URL,
        api_key="not-needed",  # vLLM doesn't need a real key
        model=settings.VLLM_MODEL,
        temperature=0.0,
        max_tokens=512,
    )

    try:
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=human_msg),
            ]
        )
        raw = response.content.strip()
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("LLM returned non-JSON. Defaulting to escalated.")
        data = {
            "verdict": "escalated",
            "category": None,
            "confidence": 0.5,
            "policy_rule_ids": [],
            "reasoning": "LLM response could not be parsed; escalating for human review.",
        }
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise

    # Apply confidence calibration threshold
    if (
        data["verdict"] == "flagged"
        and data["confidence"] < settings.CONFIDENCE_THRESHOLD
    ):
        data["verdict"] = "escalated"
        data["reasoning"] += " (Confidence below threshold — escalated.)"

    return {**state, **data}
