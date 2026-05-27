"""
Graph nodes — one function per pipeline stage.

Each node:
  - receives the full WorkflowState
  - calls the existing agent/service function unchanged
  - returns a dict of keys to merge into state
  - appends its PipelineStage record by rebuilding the list

No agent files are modified.
"""

from app.workflows.state import WorkflowState
from app.schemas.response import PipelineStage

from app.agents.intent_analyzer   import analyze_intent, intent_label
from app.agents.audience_engine   import build_audience_context
from app.agents.strategy_engine   import build_strategy
from app.agents.prompt_optimizer  import build_generation_prompt_with_context
from app.agents.content_generator import generate
from app.agents.validator         import validate
from app.agents.repair_engine     import repair, repair_humanization
from app.agents.formatter         import format_output

from app.services.experience_patterns import select_patterns, format_for_prompt as format_experience
from app.services.style_entropy        import (
    get_entropy_directives,
    format_entropy_for_prompt,
    format_banned_transitions_for_prompt,
)
from app.services.human_validator import validate_humanization
from app.services                  import content_memory

from app.context           import validate_banned
import app.context.failure_memory as failure_memory

from app.core.config import AUTO_REPAIR_THRESHOLD, HUMANIZATION_REPAIR_THRESHOLD

import logging
logger = logging.getLogger(__name__)


def _stage(name: str, status: str, detail: str) -> PipelineStage:
    return PipelineStage(stage=name, status=status, detail=detail)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Stage 1 — Intent Understanding
# ---------------------------------------------------------------------------

def intent_node(state: WorkflowState) -> dict:
    intent = analyze_intent(
        prompt=state["prompt"],
        existing_content=state.get("existing_content"),
        explicit_intent=state.get("intent_input"),
    )
    stage = _stage("intent_analysis", "completed", intent_label(intent))
    logger.info(f"Stage 1 | intent={intent}")
    return {
        "intent":   intent,
        "pipeline": [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 2 — Audience Intelligence
# ---------------------------------------------------------------------------

def audience_node(state: WorkflowState) -> dict:
    audience_context = build_audience_context(state["audience"])
    stage = _stage(
        "audience_intelligence",
        "completed",
        f"Profile matched: {audience_context['label']} ({audience_context['knowledge_level']})",
    )
    logger.info(f"Stage 2 | audience={audience_context['label']}")
    return {
        "audience_context": audience_context,
        "pipeline":         [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 3 — Use Case Strategy
# ---------------------------------------------------------------------------

def strategy_node(state: WorkflowState) -> dict:
    audience_context = state["audience_context"]
    strategy = build_strategy(
        use_case=state["use_case"],
        audience_context=audience_context,
        goal=state.get("goal", ""),
        tone=state.get("tone", "Professional"),
        style=state.get("style") or "",
    )
    platform_label = strategy["platform"].get("label", state["use_case"])
    style_label    = strategy["style"].get("label", "none") if strategy.get("style") else "none"
    stage = _stage(
        "strategy_engine",
        "completed",
        f"Platform: {platform_label} | Style: {style_label} | Target: ~{strategy['length_target']} words",
    )
    logger.info(f"Stage 3 | platform={platform_label} | style={style_label}")
    return {
        "strategy": strategy,
        "pipeline": [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 3b — Experience Pattern Selection
# ---------------------------------------------------------------------------

def experience_node(state: WorkflowState) -> dict:
    audience_context    = state["audience_context"]
    experience_patterns = select_patterns(
        audience_profile=audience_context["profile"],
        use_case=state["use_case"],
        n=2,
    )
    experience_block = format_experience(experience_patterns)
    stage = _stage(
        "experience_patterns",
        "completed",
        f"{len(experience_patterns)} domain-relevant pattern(s) selected for {audience_context['label']}",
    )
    logger.info(f"Stage 3b | experience_patterns={len(experience_patterns)}")
    return {
        "experience_patterns": experience_patterns,
        "experience_block":    experience_block,
        "pipeline":            [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 3c — Style Entropy + Content Memory
# ---------------------------------------------------------------------------

def entropy_node(state: WorkflowState) -> dict:
    entropy_directives = get_entropy_directives(n_rhythm=2, n_pacing=1, n_opener=1, n_specificity=2, n_voice=1)
    banned_block       = format_banned_transitions_for_prompt(n=16)
    entropy_block      = format_entropy_for_prompt(entropy_directives) + "\n\n" + banned_block
    memory_directive   = content_memory.get_variety_directive(use_case=state["use_case"])
    stage = _stage(
        "style_entropy",
        "completed",
        f"Per-request entropy directives applied | "
        f"Memory history: {content_memory.check_repetition().get('history_size', 0)} generations",
    )
    logger.info(f"Stage 3c | entropy directives injected | memory_directive={'yes' if memory_directive else 'none'}")
    return {
        "entropy_directives": entropy_directives,
        "entropy_block":      entropy_block,
        "memory_directive":   memory_directive or "",
        "pipeline":           [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 3d — Context Assembly + Pre-Generation Validation
# Stage 4  — Prompt Optimization (inline — ContextPackage.to_prompt())
# ---------------------------------------------------------------------------

def context_node(state: WorkflowState) -> dict:
    optimized_prompt, context_package = build_generation_prompt_with_context(
        topic=state["prompt"],
        intent=state["intent"],
        audience=state["audience"],
        use_case=state["use_case"],
        style=state.get("style") or "",
        existing_content=state.get("existing_content") or "",
        target_use_case=state.get("target_use_case") or "",
        feedback="",
        experience_block=state["experience_block"],
        entropy_block=state["entropy_block"],
        memory_directive=state.get("memory_directive") or "",
    )
    pre_check = context_package.validate_pre_generation()

    pre_check_detail = "Pre-generation check: passed"
    if not pre_check.passed:
        pre_check_detail = f"Pre-generation check: ISSUES — {' | '.join(pre_check.issues)}"
    if pre_check.banned_in_topic:
        pre_check_detail += f" | Banned phrases in topic: {pre_check.banned_in_topic[:3]}"
    if pre_check.warnings:
        pre_check_detail += f" | Warnings: {pre_check.warnings[0]}"

    stage_context = _stage("context_assembly",  "completed", pre_check_detail)
    stage_prompt  = _stage(
        "prompt_optimizer",
        "completed",
        f"Context-engine prompt: {len(optimized_prompt)} chars | {len(optimized_prompt.split())} words",
    )
    logger.info(f"Stage 3d | context assembled | pre_check_passed={pre_check.passed}")
    logger.info(f"Stage 4  | prompt={len(optimized_prompt)} chars")
    return {
        "optimized_prompt": optimized_prompt,
        "context_package":  context_package,
        "pre_check":        pre_check,
        "pipeline":         [*state.get("pipeline", []), stage_context, stage_prompt],
    }


# ---------------------------------------------------------------------------
# Stage 5 — Content Generation
# ---------------------------------------------------------------------------

def generate_node(state: WorkflowState) -> dict:
    draft = generate(
        prompt=state["optimized_prompt"],
        use_case=state["use_case"],
        style=state.get("style") or "",
    )
    stage = _stage(
        "content_generator",
        "completed",
        f"Draft generated: {len(draft)} chars | {len(draft.split())} words",
    )
    logger.info(f"Stage 5 | draft={len(draft)} chars")
    return {
        "draft":           draft,
        "working_content": draft,      # set working_content = draft; 5c may update it
        "pipeline":        [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 5b — Humanization Validation
# ---------------------------------------------------------------------------

def humanize_validate_node(state: WorkflowState) -> dict:
    humanization_result = validate_humanization(state["draft"])
    stage_validate = _stage(
        "humanization_validator",
        "completed",
        f"Humanization score: {humanization_result.score}/100 ({humanization_result.grade}) | "
        f"Spec={humanization_result.specificity_score} "
        f"Tension={humanization_result.tension_score} "
        f"Orig={humanization_result.originality_score} "
        f"Exp={humanization_result.experience_score}",
    )
    logger.info(f"Stage 5b | humanization={humanization_result.score} grade={humanization_result.grade}")

    new_pipeline = [*state.get("pipeline", []), stage_validate]

    # When repair will NOT run (score above threshold), record the skip now so the
    # pipeline trace is identical to the original sequential workflow.
    if humanization_result.score >= HUMANIZATION_REPAIR_THRESHOLD:
        stage_skip = _stage(
            "humanization_repair",
            "skipped",
            f"Score {humanization_result.score} >= threshold {HUMANIZATION_REPAIR_THRESHOLD}",
        )
        new_pipeline = [*new_pipeline, stage_skip]
        logger.info(f"Stage 5c | skipped | score {humanization_result.score} >= {HUMANIZATION_REPAIR_THRESHOLD}")

    return {
        "humanization_result": humanization_result,
        "pipeline":            new_pipeline,
    }


# ---------------------------------------------------------------------------
# Stage 5c — Humanization Repair  (only reached when score < threshold)
# ---------------------------------------------------------------------------

def humanize_repair_node(state: WorkflowState) -> dict:
    strategy = state["strategy"]
    audience_context = state["audience_context"]
    human_repair_ctx = {
        "platform": strategy["platform"],
        "audience": audience_context["profile"],
        "tone":     state.get("tone"),
        "use_case": state["use_case"],
    }
    humanization_result = state["humanization_result"]
    working_content, humanization_repaired = repair_humanization(
        content=state["draft"],
        humanization=humanization_result,
        ctx=human_repair_ctx,
    )
    if humanization_repaired:
        humanization_result = validate_humanization(working_content)
        stage = _stage(
            "humanization_repair",
            "completed",
            f"Humanization repaired | New score: {humanization_result.score}/100 ({humanization_result.grade})",
        )
        logger.info(f"Stage 5c | humanization repair applied | new_score={humanization_result.score}")
    else:
        stage = _stage("humanization_repair", "skipped", "No humanization changes made in this pass")

    return {
        "working_content":       working_content,
        "humanization_result":   humanization_result,
        "humanization_repaired": humanization_repaired,
        "pipeline":              [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 6 — Quality Validation
# ---------------------------------------------------------------------------

def quality_validate_node(state: WorkflowState) -> dict:
    strategy         = state["strategy"]
    audience_context = state["audience_context"]
    validation_ctx   = {
        "use_case": state["use_case"],
        "platform": strategy["platform"],
        "audience": audience_context["profile"],
        "tone":     state.get("tone"),
    }
    validation = validate(state["working_content"], validation_ctx)
    stage_validate = _stage(
        "validator",
        "completed",
        f"Quality score: {validation.score}/100 ({validation.grade}) | "
        f"Failures: {len(validation.failures)} | Warnings: {len(validation.warnings)}",
    )
    logger.info(
        f"Stage 6 | score={validation.score} | grade={validation.grade} | "
        f"failures={len(validation.failures)}"
    )

    new_pipeline = [*state.get("pipeline", []), stage_validate]

    # When repair will NOT run, record the skip now so the pipeline trace is
    # identical to the original sequential workflow.
    needs_repair = validation.score < AUTO_REPAIR_THRESHOLD and bool(validation.failures)
    if not needs_repair:
        skip_reason = (
            f"Score {validation.score} >= threshold {AUTO_REPAIR_THRESHOLD}"
            if validation.score >= AUTO_REPAIR_THRESHOLD
            else "No failures to repair"
        )
        stage_skip = _stage("repair_engine", "skipped", skip_reason)
        new_pipeline = [*new_pipeline, stage_skip]
        logger.info(f"Stage 7 | skipped | {skip_reason}")

    return {
        "validation": validation,
        "pipeline":   new_pipeline,
    }


# ---------------------------------------------------------------------------
# Stage 7 — Quality Repair  (only reached when score < threshold and failures exist)
# ---------------------------------------------------------------------------

def quality_repair_node(state: WorkflowState) -> dict:
    strategy         = state["strategy"]
    audience_context = state["audience_context"]
    validation       = state["validation"]
    validation_ctx   = {
        "use_case": state["use_case"],
        "platform": strategy["platform"],
        "audience": audience_context["profile"],
        "tone":     state.get("tone"),
    }
    final, quality_repaired = repair(state["working_content"], validation, validation_ctx)
    if quality_repaired:
        stage = _stage(
            "repair_engine",
            "completed",
            f"Repaired {len(validation.failures)} issue(s) — deterministic + LLM surgical fixes applied",
        )
        logger.info("Stage 7 | quality repair applied")
    else:
        stage = _stage("repair_engine", "skipped", "No auto-repairable issues found in this pass")

    return {
        "final":           final,
        "quality_repaired": quality_repaired,
        "pipeline":         [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 8 — Final Formatting
# ---------------------------------------------------------------------------

def format_node(state: WorkflowState) -> dict:
    strategy       = state["strategy"]
    platform_label = strategy["platform"].get("label", state["use_case"])
    # Use final if quality repair ran, otherwise working_content
    content_to_format = state.get("final") or state["working_content"]
    final = format_output(content_to_format, state["use_case"], strategy["platform"])
    stage = _stage(
        "formatter",
        "completed",
        f"Platform-native formatting applied for {platform_label}",
    )
    logger.info(f"Stage 8 | formatting complete | {len(final)} chars")
    return {
        "final":    final,
        "pipeline": [*state.get("pipeline", []), stage],
    }


# ---------------------------------------------------------------------------
# Stage 8b — Memory Registration + Failure Recording
# ---------------------------------------------------------------------------

def memory_node(state: WorkflowState) -> dict:
    context_package      = state["context_package"]
    humanization_result  = state["humanization_result"]
    validation           = state["validation"]
    final                = state["final"]
    humanization_repaired = state.get("humanization_repaired", False)
    quality_repaired      = state.get("quality_repaired", False)
    was_repaired          = humanization_repaired or quality_repaired

    content_memory.register(final, use_case=state["use_case"])

    all_validator_issues = [f.check for f in validation.failures] if validation.failures else []
    platform_violations  = context_package.platform.validate_output(final)
    banned_in_output     = validate_banned(
        final,
        platform_id=context_package.platform.id,
        audience_id=context_package.audience.id,
    )
    has_any_failure = (
        all_validator_issues or
        humanization_result.issues or
        platform_violations or
        banned_in_output
    )
    if has_any_failure:
        failure_memory.record(
            use_case=state["use_case"],
            audience_id=context_package.audience.id,
            validator_issues=all_validator_issues,
            humanization_issues=humanization_result.issues,
            platform_violations=platform_violations,
            banned_phrases_found=banned_in_output,
            score=humanization_result.score,
            repaired=was_repaired,
        )
    logger.info(
        f"Stage 8b | memory registered | failures_recorded={has_any_failure} | "
        f"platform_violations={len(platform_violations)} | banned_in_output={len(banned_in_output)}"
    )
    # memory_node has side-effects only — no new state keys
    return {}
