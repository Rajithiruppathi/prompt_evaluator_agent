"""
Content Workflow — LangGraph Pipeline Orchestrator

Pipeline stages (13 total) — now executed as a compiled StateGraph:

  1.  Intent Understanding         → detect create / improve / rewrite / convert
  2.  Audience Intelligence        → match audience profile
  3.  Use Case Strategy            → select platform rules + style
  3b. Experience Pattern Selection → pick domain-relevant production scenarios
  3c. Style Entropy + Memory       → per-request variation directives + anti-repetition
  3d. Context Assembly             → build ContextPackage + pre-generation validation
  4.  Prompt Optimization          → context-engine prompt (ContextPackage.to_prompt())
  5.  Content Generation           → call LLM
  5b. Humanization Validation      → score experiential realism, specificity, originality
  5c. Humanization Repair          → surgical fix if humanization score < threshold
  6.  Quality Validation           → 13-check deterministic quality scoring
  7.  Quality Auto-Repair          → fix failing checks if score < threshold
  8.  Final Formatting             → platform-native structure
  8b. Memory Registration + Failure Recording → anti-repetition + failure-aware generation

Returns a ContentResponse with full pipeline trace and both quality and
humanization scores. The public interface (run) is unchanged.
"""

from app.schemas.request  import ContentRequest
from app.schemas.response import ContentResponse, HumanizationResult

from app.workflows.state import WorkflowState
from app.workflows.graph import _graph

import logging
logger = logging.getLogger(__name__)


def run(request: ContentRequest) -> ContentResponse:
    """
    Execute the full content pipeline via the compiled LangGraph StateGraph.

    Handles all four intent modes (create, improve, rewrite, convert).
    Returns a complete ContentResponse with pipeline trace, quality metrics,
    and humanization scores.
    """
    logger.info(
        f"Pipeline start | use_case={request.use_case} | audience={request.audience} | "
        f"intent={request.intent or 'auto'} | style={request.style or 'none'}"
    )

    # ── Build initial state from request ──────────────────────────────────────
    initial_state: WorkflowState = {
        "prompt":                request.prompt,
        "use_case":              request.use_case,
        "audience":              request.audience,
        "goal":                  request.goal,
        "tone":                  request.tone,
        "style":                 request.style,
        "intent_input":          request.intent,
        "existing_content":      request.existing_content,
        "target_use_case":       request.target_use_case,
        "humanization_repaired": False,
        "quality_repaired":      False,
        "pipeline":              [],
    }

    # ── Invoke graph ──────────────────────────────────────────────────────────
    state = _graph.invoke(initial_state)

    # ── Unpack state ──────────────────────────────────────────────────────────
    intent               = state["intent"]
    audience_context     = state["audience_context"]
    strategy             = state["strategy"]
    optimized_prompt     = state["optimized_prompt"]
    draft                = state["draft"]
    final                = state["final"]
    validation           = state["validation"]
    humanization_result  = state["humanization_result"]
    experience_patterns  = state["experience_patterns"]
    entropy_directives   = state["entropy_directives"]
    humanization_repaired = state.get("humanization_repaired", False)
    quality_repaired      = state.get("quality_repaired", False)
    pipeline              = state.get("pipeline", [])

    was_repaired = humanization_repaired or quality_repaired

    # ── Build HumanizationResult for response schema ──────────────────────────
    humanization_response = HumanizationResult(
        score=humanization_result.score,
        grade=humanization_result.grade,               # type: ignore[arg-type]
        specificity_score=humanization_result.specificity_score,
        tension_score=humanization_result.tension_score,
        originality_score=humanization_result.originality_score,
        experience_score=humanization_result.experience_score,
        issues=humanization_result.issues,
        suggestions=humanization_result.suggestions,
    )

    platform_label = strategy["platform"].get("label", request.use_case)
    style_label    = strategy["style"].get("label", "none") if strategy.get("style") else "none"

    # ── Assemble response ─────────────────────────────────────────────────────
    return ContentResponse(
        intent=intent,
        use_case=request.use_case,
        audience=audience_context["label"],
        audience_profile=audience_context["profile"]["id"],
        style=request.style,
        tone=request.tone,
        optimized_prompt=optimized_prompt,
        draft_output=draft,
        final_output=final,
        validation=validation,
        humanization=humanization_response,
        repaired=was_repaired,
        pipeline=pipeline,
        metadata={
            "platform_profile":      strategy["platform"].get("id", "general"),
            "style_profile":         strategy.get("style", {}).get("id", "none"),
            "audience_profile":      audience_context["profile"]["id"],
            "draft_words":           len(draft.split()),
            "final_words":           len(final.split()),
            "validation_score":      validation.score,
            "humanization_score":    humanization_result.score,
            "humanization_grade":    humanization_result.grade,
            "humanization_repaired": humanization_repaired,
            "quality_repaired":      quality_repaired,
            "entropy_directives":    list(entropy_directives.keys()),
            "experience_patterns":   [p["id"] for p in experience_patterns],
        },
    )
