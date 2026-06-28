"""
LangGraph orchestrator — routes content to specialist agents and aggregates verdicts.

Graph:
  START → detect_modality → [text_agent | image_agent | audio_agent]
                                         ↓
                              rag_policy_lookup → llm_verdict → calibrate → END
"""

from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END

from app.agents.text_agent import analyse_text
from app.agents.image_agent import analyse_image
from app.agents.audio_agent import analyse_audio
from app.agents.rag_agent import retrieve_policy
from app.agents.verdict_agent import generate_verdict
from app.core.config import settings


class PipelineState(TypedDict):
    # inputs
    text: Optional[str]
    file_bytes: Optional[bytes]
    mime_type: Optional[str]
    # routing
    modality: Optional[Literal["text", "image", "audio"]]
    # intermediate
    content_summary: Optional[str]  # normalised text representation
    policy_chunks: Optional[list]
    # output
    verdict: Optional[str]
    category: Optional[str]
    confidence: Optional[float]
    policy_rule_ids: Optional[list[str]]
    reasoning: Optional[str]


def detect_modality(state: PipelineState) -> PipelineState:
    mime = state.get("mime_type", "")
    if mime.startswith("image/"):
        modality = "image"
    elif mime.startswith("audio/") or mime.startswith("video/"):
        modality = "audio"
    else:
        modality = "text"
    return {**state, "modality": modality}


def route_by_modality(state: PipelineState) -> str:
    return state["modality"]


async def run_pipeline(payload: dict) -> dict:
    graph = StateGraph(PipelineState)

    graph.add_node("detect_modality", detect_modality)
    graph.add_node("text_agent", analyse_text)
    graph.add_node("image_agent", analyse_image)
    graph.add_node("audio_agent", analyse_audio)
    graph.add_node("rag_lookup", retrieve_policy)
    graph.add_node("verdict", generate_verdict)

    graph.set_entry_point("detect_modality")
    graph.add_conditional_edges(
        "detect_modality",
        route_by_modality,
        {"text": "text_agent", "image": "image_agent", "audio": "audio_agent"},
    )
    for agent in ["text_agent", "image_agent", "audio_agent"]:
        graph.add_edge(agent, "rag_lookup")
    graph.add_edge("rag_lookup", "verdict")
    graph.add_edge("verdict", END)

    app = graph.compile()
    initial_state = PipelineState(
        text=payload.get("text"),
        file_bytes=payload.get("file_bytes"),
        mime_type=payload.get("mime_type"),
        modality=None,
        content_summary=None,
        policy_chunks=None,
        verdict=None,
        category=None,
        confidence=None,
        policy_rule_ids=None,
        reasoning=None,
    )
    final_state = await app.ainvoke(initial_state)

    return {
        "verdict": final_state["verdict"],
        "category": final_state["category"],
        "confidence": final_state["confidence"],
        "policy_rule_ids": final_state["policy_rule_ids"],
        "reasoning": final_state["reasoning"],
        "modality": final_state["modality"],
    }
