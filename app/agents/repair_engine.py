"""
Stage 7 — Auto-Repair Engine (upgraded)

Two repair modes:

  Quality Repair (original)
  ─────────────────────────
  Triggered when validation score < AUTO_REPAIR_THRESHOLD.
  1. Deterministic: trim hashtags, trim length, fix exclamations.
  2. LLM surgical: targeted fix for remaining high/critical failures.

  Humanization Repair (new)
  ─────────────────────────
  Triggered when humanization score < HUMANIZATION_REPAIR_THRESHOLD.
  1. Deterministic: replace the most common robotic transitions in-place.
  2. LLM humanization pass: rewrite to inject specificity, tension,
     and experiential voice — without altering structure or core message.

Repair principle: fix ONLY what failed. Preserve everything else.
"""

import re
from typing import Optional

from app.core.llm import repair_llm
from app.core.prompts import bullet_list, assemble
from app.schemas.response import ValidationResult, ValidationFailure
from app.services.human_validator import HumanizationResult

import logging
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Quality repairs — deterministic, no LLM
# ---------------------------------------------------------------------------

_DETERMINISTIC_CHECKS = {"hashtag_count", "content_length", "exclamations"}


def _trim_hashtags(content: str, target_max: int) -> str:
    tags = re.findall(r"#\w+", content)
    if len(tags) <= target_max:
        return content
    keep = tags[:target_max]
    content_no_tags = re.sub(r"\s*#\w+", "", content).strip()
    return content_no_tags + "\n\n" + " ".join(keep)


def _trim_to_length(content: str, max_words: int) -> str:
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(content.split()) <= max_words or len(paragraphs) <= 2:
        return content
    middle = paragraphs[1:-1]
    if not middle:
        return content
    shortest_idx = min(range(len(middle)), key=lambda i: len(middle[i].split()))
    del middle[shortest_idx]
    return "\n\n".join([paragraphs[0]] + middle + [paragraphs[-1]])


def _fix_exclamations(content: str, max_allowed: int = 2) -> str:
    count = content.count("!")
    if count <= max_allowed:
        return content
    indices = [i for i, c in enumerate(content) if c == "!"]
    to_replace = indices[:count - max_allowed]
    content_list = list(content)
    for idx in to_replace:
        content_list[idx] = "."
    return "".join(content_list)


def _apply_deterministic_repairs(
    content: str,
    failures: list[ValidationFailure],
    ctx: dict,
) -> tuple[str, list[str]]:
    """Apply no-LLM repairs. Returns (repaired_content, list_of_fixed_checks)."""
    repaired = content
    fixed: list[str] = []
    platform = ctx.get("platform", {})

    for failure in failures:
        if failure.check == "hashtag_count":
            rule = platform.get("validation", {}).get("hashtag_count", {})
            max_h = rule.get("max", 5)
            current_tags = re.findall(r"#\w+", repaired)
            if len(current_tags) > max_h:
                repaired = _trim_hashtags(repaired, max_h)
                fixed.append("hashtag_count")

        elif failure.check == "content_length":
            max_words = platform.get("validation", {}).get("max_words", 99999)
            if len(repaired.split()) > max_words:
                repaired = _trim_to_length(repaired, max_words)
                fixed.append("content_length")

        elif failure.check == "exclamations":
            repaired = _fix_exclamations(repaired)
            fixed.append("exclamations")

    return repaired, fixed


# ---------------------------------------------------------------------------
# Quality LLM repair
# ---------------------------------------------------------------------------

def _build_quality_repair_prompt(
    content: str,
    failures: list[ValidationFailure],
    ctx: dict,
) -> str:
    issue_list      = bullet_list([f.message for f in failures])
    suggestion_list = bullet_list([f.suggestion for f in failures])
    audience  = ctx.get("audience", {})
    platform  = ctx.get("platform", {})

    return f"""You are a senior editor performing a surgical edit. Fix ONLY the listed issues. Preserve everything else.

CONTENT TO REPAIR:
{content}

ISSUES TO FIX:
{issue_list}

HOW TO FIX EACH:
{suggestion_list}

CONTEXT:
Platform: {platform.get('label', '')}
Audience: {audience.get('label', '')}
Tone: {ctx.get('tone', 'Professional')}

EDITING RULES:
  • Fix ONLY the specific issues listed — do not restructure the whole piece
  • Keep the author's voice intact — sharpen it, do not replace it
  • Preserve the core ideas and structure
  • Replace clichés with what was specifically meant — not with other clichés
  • If fake statistics are flagged, remove the claim or rewrite as direct observation
  • If the hook is weak, rewrite only the first 1-2 lines
  • If the CTA is weak, rewrite only the last 1-2 lines

Return ONLY the repaired content. No preamble. No labels. No commentary.
Start with the first word of the content."""


# ---------------------------------------------------------------------------
# Humanization repairs — deterministic transition substitution
# ---------------------------------------------------------------------------

_ROBOTIC_SUBSTITUTIONS: dict[str, str] = {
    "here's why that matters": "",     # delete — the following sentence should carry the weight
    "here's the thing": "",
    "here's what i mean": "",
    "the reality is": "",
    "the truth is": "",
    "the fact of the matter is": "",
    "it's important to note that": "",
    "it is important to note that": "",
    "it's worth noting that": "",
    "it's worth mentioning that": "",
    "simply put,": "",
    "in other words,": "",
    "to be clear,": "",
    "the bottom line is": "",
    "let me explain": "",
    "at the end of the day,": "",
    "at the end of the day": "",
    "as we all know,": "",
    "as we all know": "",
    "needless to say,": "",
    "needless to say": "",
    "that being said,": "",
    "that being said": "",
    "having said that,": "",
    "having said that": "",
    "first and foremost,": "",
    "first and foremost": "",
    "last but not least,": "",
    "last but not least": "",
    "in a nutshell,": "",
    "in a nutshell": "",
    "all things considered,": "",
    "all things considered": "",
    "long story short,": "",
    "long story short": "",
    "believe it or not,": "",
    "believe it or not": "",
}


def _fix_robotic_transitions(content: str) -> tuple[str, int]:
    """
    Deterministically remove the most common robotic transition phrases.

    Removing them (instead of replacing with alternatives) forces the
    surrounding sentences to carry their own weight — which is stronger.
    Returns (cleaned_content, number_of_substitutions_made).
    """
    result = content
    count = 0
    for phrase, replacement in _ROBOTIC_SUBSTITUTIONS.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        new_result, n = pattern.subn(replacement, result)
        count += n
        result = new_result

    # Clean up any double spaces or awkward punctuation left behind
    result = re.sub(r"  +", " ", result)
    result = re.sub(r"\. \.", ".", result)
    result = re.sub(r",\s*,", ",", result)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip(), count


# ---------------------------------------------------------------------------
# Humanization LLM repair
# ---------------------------------------------------------------------------

def _build_humanization_repair_prompt(
    content: str,
    humanization: HumanizationResult,
    ctx: dict,
) -> str:
    """Build a targeted humanization repair instruction."""
    audience = ctx.get("audience", {})
    platform = ctx.get("platform", {})
    issues   = bullet_list(humanization.issues) if humanization.issues else "  • General AI-template rhythm detected"
    suggestions = bullet_list(humanization.suggestions) if humanization.suggestions else ""

    dimension_scores = (
        f"  Specificity:   {humanization.specificity_score}/25\n"
        f"  Narrative tension: {humanization.tension_score}/25\n"
        f"  Originality:   {humanization.originality_score}/25\n"
        f"  Experiential:  {humanization.experience_score}/25"
    )

    return f"""You are a developmental editor specializing in making AI-generated content read as if a real practitioner wrote it.

Your job is a surgical humanization edit — not a rewrite. Preserve the structure, argument, and core ideas exactly. Fix only what makes this feel like AI output.

CONTENT TO HUMANIZE:
{content}

HUMANIZATION SCORE: {humanization.score}/100 (grade: {humanization.grade})
{dimension_scores}

ISSUES DETECTED:
{issues}

HOW TO FIX THEM:
{suggestions}

HUMANIZATION RULES — apply these in order of priority:

1. SPECIFICITY: If the content is vague, add one concrete detail — a number, a named tool, a timeline.
   Do not invent facts. Use a plausible, realistic detail of the kind that a practitioner would naturally include.

2. NARRATIVE TENSION: If the content is declarative without friction, add one moment of contrast.
   A thing that went wrong. A counterintuitive outcome. A tradeoff that wasn't obvious.

3. VOICE: Remove any remaining filler transitions. If a sentence starts with a robotic phrase,
   cut the phrase and let the sentence stand on its own — or cut the sentence.

4. RHYTHM: Break any sequence of three sentences with similar length or structure.
   One short. One longer. Vary deliberately.

5. ORIGINALITY: Replace any generic claim with the specific version.
   "leveraging AI" → name the actual mechanism. "proven results" → name the actual result.

HARD CONSTRAINTS:
  • Do NOT restructure the content — same sections, same order
  • Do NOT change the central argument or core message
  • Do NOT add new sections or headers
  • Do NOT make the content longer than the original by more than 15%
  • Do NOT fabricate statistics, company names, or specific events
  • Do NOT add exclamation marks

Platform: {platform.get('label', 'General')}
Audience: {audience.get('label', 'Professional')}

Return ONLY the humanized content. No preamble. No commentary. No labels.
Start with the first word of the content."""


def _llm_humanization_repair(
    content: str,
    humanization: HumanizationResult,
    ctx: dict,
) -> str:
    instruction = _build_humanization_repair_prompt(content, humanization, ctx)
    llm = repair_llm()
    response = llm.invoke(instruction)
    return str(response.content).strip()


def repair_humanization(
    content: str,
    humanization: HumanizationResult,
    ctx: dict,
) -> tuple[str, bool]:
    """
    Repair content to improve its humanization score.

    Phase 1: Deterministic — remove robotic transitions in-place.
    Phase 2: LLM pass — inject specificity, tension, and experiential voice.

    Returns (repaired_content, was_modified: bool).
    """
    repaired = content
    any_change = False

    # Phase 1: Remove robotic transitions deterministically
    cleaned, n_subs = _fix_robotic_transitions(repaired)
    if n_subs > 0:
        repaired = cleaned
        any_change = True
        logger.info(f"Humanization deterministic: removed {n_subs} robotic transition(s)")

    # Phase 2: LLM humanization pass for deeper issues
    needs_llm = (
        humanization.specificity_score < 12 or
        humanization.tension_score < 10 or
        humanization.experience_score < 10
    )
    if needs_llm:
        logger.info(
            f"Humanization LLM repair | "
            f"spec={humanization.specificity_score} tension={humanization.tension_score} "
            f"exp={humanization.experience_score}"
        )
        repaired = _llm_humanization_repair(repaired, humanization, ctx)
        any_change = True

    return repaired, any_change


# ---------------------------------------------------------------------------
# Quality repair — public API (original, unchanged interface)
# ---------------------------------------------------------------------------

def repair(
    content: str,
    validation: ValidationResult,
    ctx: dict,
) -> tuple[str, bool]:
    """
    Repair content based on quality validation failures.

    Strategy:
      1. Deterministic repairs first (fast, no API cost)
      2. Targeted LLM pass for remaining high/critical failures

    Returns (repaired_content, was_repaired: bool).
    """
    critical_failures = [f for f in validation.failures if f.severity == "critical"]
    high_failures     = [f for f in validation.failures if f.severity == "high"]
    all_key_failures  = critical_failures + high_failures

    if not all_key_failures:
        logger.info("No high/critical failures — skipping quality repair")
        return content, False

    repaired = content
    any_repair = False

    # Step 1: Deterministic repairs
    repaired, fixed = _apply_deterministic_repairs(repaired, all_key_failures, ctx)
    if fixed:
        logger.info(f"Quality deterministic repairs: {', '.join(fixed)}")
        any_repair = True

    # Step 2: LLM repair for remaining non-deterministic failures
    remaining = [f for f in all_key_failures if f.check not in fixed]
    if remaining:
        logger.info(f"Quality LLM repair for {len(remaining)} issue(s): {[f.check for f in remaining]}")
        instruction = _build_quality_repair_prompt(repaired, remaining, ctx)
        llm = repair_llm()
        repaired = str(llm.invoke(instruction).content).strip()
        any_repair = True

    return repaired, any_repair
