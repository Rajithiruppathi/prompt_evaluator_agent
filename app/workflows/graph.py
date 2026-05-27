"""
StateGraph assembly — builds and compiles the LangGraph content pipeline.

The compiled graph is a module-level singleton (_graph) so it is built once
at import time and reused across requests, matching the existing LLM client
lifecycle in app/core/llm.py.
"""

from langgraph.graph import StateGraph, END

from app.workflows.state import WorkflowState
from app.workflows.nodes import (
    intent_node,
    audience_node,
    strategy_node,
    experience_node,
    entropy_node,
    context_node,
    generate_node,
    humanize_validate_node,
    humanize_repair_node,
    quality_validate_node,
    quality_repair_node,
    format_node,
    memory_node,
)
from app.core.config import AUTO_REPAIR_THRESHOLD, HUMANIZATION_REPAIR_THRESHOLD


# ---------------------------------------------------------------------------
# Conditional edge routing functions
# ---------------------------------------------------------------------------

def route_humanization(state: WorkflowState) -> str:
    """After Stage 5b: branch to repair if humanization score is below threshold."""
    if state["humanization_result"].score < HUMANIZATION_REPAIR_THRESHOLD:
        return "humanize_repair"
    return "quality_validate"


def route_quality(state: WorkflowState) -> str:
    """After Stage 6: branch to repair if quality score is below threshold and failures exist."""
    v = state["validation"]
    if v.score < AUTO_REPAIR_THRESHOLD and v.failures:
        return "quality_repair"
    return "format"


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph():
    g = StateGraph(WorkflowState)

    # ── Register nodes ────────────────────────────────────────────────────────
    g.add_node("intent",            intent_node)
    g.add_node("audience",          audience_node)
    g.add_node("strategy",          strategy_node)
    g.add_node("experience",        experience_node)
    g.add_node("entropy",           entropy_node)
    g.add_node("context",           context_node)
    g.add_node("generate",          generate_node)
    g.add_node("humanize_validate", humanize_validate_node)
    g.add_node("humanize_repair",   humanize_repair_node)
    g.add_node("quality_validate",  quality_validate_node)
    g.add_node("quality_repair",    quality_repair_node)
    g.add_node("format",            format_node)
    g.add_node("memory",            memory_node)

    # ── Wire edges ────────────────────────────────────────────────────────────
    g.set_entry_point("intent")

    g.add_edge("intent",   "audience")
    g.add_edge("audience", "strategy")
    g.add_edge("strategy", "experience")
    g.add_edge("experience", "entropy")
    g.add_edge("entropy",  "context")
    g.add_edge("context",  "generate")
    g.add_edge("generate", "humanize_validate")

    # Conditional: humanization repair branch
    g.add_conditional_edges(
        "humanize_validate",
        route_humanization,
        {
            "humanize_repair":  "humanize_repair",
            "quality_validate": "quality_validate",
        },
    )
    g.add_edge("humanize_repair", "quality_validate")

    # Conditional: quality repair branch
    g.add_conditional_edges(
        "quality_validate",
        route_quality,
        {
            "quality_repair": "quality_repair",
            "format":         "format",
        },
    )
    g.add_edge("quality_repair", "format")

    g.add_edge("format",  "memory")
    g.add_edge("memory",  END)

    return g.compile()


# Module-level singleton — built once at import time
_graph = build_graph()
