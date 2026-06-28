"""
Unit tests for the verdict agent JSON parsing logic.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_verdict_agent_parses_valid_json():
    from app.agents.verdict_agent import generate_verdict

    mock_response_content = json.dumps({
        "verdict": "flagged",
        "category": "spam",
        "confidence": 0.95,
        "policy_rule_ids": ["SP-001"],
        "reasoning": "The content is a clear commercial spam solicitation.",
    })

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AsyncMock(content=mock_response_content)

    state = {
        "content_summary": "Buy 10k followers for $5 now!",
        "policy_chunks": [{"rule_id": "SP-001", "text": "Spam is prohibited.", "score": 0.9}],
    }

    with patch("app.agents.verdict_agent.ChatOpenAI", return_value=mock_llm):
        result = await generate_verdict(state)

    assert result["verdict"] == "flagged"
    assert result["category"] == "spam"
    assert result["confidence"] == 0.95
    assert "SP-001" in result["policy_rule_ids"]


@pytest.mark.asyncio
async def test_verdict_agent_escalates_on_bad_json():
    from app.agents.verdict_agent import generate_verdict

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AsyncMock(content="Sorry, I cannot help with that.")

    state = {
        "content_summary": "Some content",
        "policy_chunks": [],
    }

    with patch("app.agents.verdict_agent.ChatOpenAI", return_value=mock_llm):
        result = await generate_verdict(state)

    assert result["verdict"] == "escalated"


def test_config_loads():
    from app.core.config import settings
    assert settings.CONFIDENCE_THRESHOLD == 0.75
    assert settings.POSTGRES_DB == "sentinel"
