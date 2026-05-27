"""
WorkflowState — shared state bag for the LangGraph content pipeline.

Keys are added progressively as the graph executes. total=False means every
key is optional so nodes can start with a sparse initial dict.

Serialisation note: context_package, humanization_result, and validation are
live in-process objects only — they are never checkpointed or persisted.
"""

from typing import Any, Optional
from typing_extensions import TypedDict


class WorkflowState(TypedDict, total=False):
    # ── Inputs (populated once from ContentRequest before graph.invoke) ───────
    prompt:           str
    use_case:         str
    audience:         str
    goal:             str
    tone:             str
    style:            Optional[str]
    intent_input:     Optional[str]     # request.intent — may be None (auto-detect)
    existing_content: Optional[str]
    target_use_case:  Optional[str]

    # ── Stage 1: Intent Understanding ─────────────────────────────────────────
    intent: str                         # "create" | "improve" | "rewrite" | "convert"

    # ── Stage 2: Audience Intelligence ────────────────────────────────────────
    audience_context: dict              # {label, knowledge_level, profile}

    # ── Stage 3: Use Case Strategy ────────────────────────────────────────────
    strategy: dict                      # {platform, style, length_target}

    # ── Stage 3b: Experience Patterns ─────────────────────────────────────────
    experience_patterns: list
    experience_block:    str

    # ── Stage 3c: Style Entropy + Memory ──────────────────────────────────────
    entropy_directives: dict
    entropy_block:      str
    memory_directive:   str

    # ── Stage 3d: Context Assembly ────────────────────────────────────────────
    optimized_prompt: str
    context_package:  Any              # ContextPackage — live object, not serialisable
    pre_check:        Any              # PreGenerationCheck result

    # ── Stage 5: Content Generation ───────────────────────────────────────────
    draft: str

    # ── Stage 5b: Humanization Validation ─────────────────────────────────────
    humanization_result: Any           # HumanizationScore from human_validator

    # ── Stage 5c: Humanization Repair ─────────────────────────────────────────
    humanization_repaired: bool
    working_content:       str         # equals draft, or repaired draft after 5c

    # ── Stage 6: Quality Validation ───────────────────────────────────────────
    validation: Any                    # ValidationResult

    # ── Stage 7: Quality Repair ───────────────────────────────────────────────
    quality_repaired: bool
    final:            str              # working_content after optional quality repair

    # ── Pipeline trace (cumulative) ───────────────────────────────────────────
    pipeline: list                     # list[PipelineStage] — appended by every node
