"""
Stage 6 — Validation Pipeline

Deterministic quality scoring across 13 check categories.
No LLM calls — all checks are programmatic and reproducible.

Score: 0-100. Higher is better.
  90-100 → Excellent — ready to publish
  75-89  → Good — passes threshold, minor polish optional
  55-74  → Fair — noticeable issues, repair recommended
  0-54   → Poor — major quality problems, repair required

Check categories:
  1. AI cliché detection
  2. Generic phrase detection
  3. Weak opener detection
  4. Fake statistic patterns
  5. Sentence length variance
  6. Repetition detection
  7. Exclamation mark overuse
  8. CTA presence and quality
  9. Platform-specific structure (hashtags, length, title, paragraphs)
  10. Passive voice overuse
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Callable

from app.knowledge.examples.content_examples import (
    AI_CLICHES, GENERIC_PHRASES, FAKE_STAT_PATTERNS,
)
from app.schemas.response import ValidationFailure, ValidationResult


# ---------------------------------------------------------------------------
# Scoring weights — total deductions are capped per category
# ---------------------------------------------------------------------------
_W = {
    "ai_cliche":        3,    # per phrase, cap 24
    "generic":          4,    # per phrase, cap 20
    "weak_opener":      15,   # binary
    "fake_stat":        8,    # per pattern found, cap 16
    "long_sentences":   5,    # binary
    "repetition":       5,    # per phrase, cap 15
    "exclamations":     3,    # per excess mark, cap 9
    "no_cta":           10,   # binary
    "hashtag_wrong":    8,    # binary
    "too_long":         8,    # binary
    "no_title":         10,   # binary (blog only)
    "long_paragraphs":  4,    # per para, cap 12
    "passive_voice":    4,    # binary (3+ instances)
}

_WEAK_CTA_SIGNALS = [
    "let me know", "what do you think", "share if you agree",
    "feel free to reach out", "don't hesitate to contact",
    "looking forward to hearing", "like and share", "follow for more",
    "subscribe for more", "thoughts?", "hope this helps",
    "let me know your thoughts", "drop a comment",
]

_PASSIVE_RE = re.compile(
    r"\b(was|were|is|are|been|being)\s+\w+ed\b",
    re.IGNORECASE,
)

_WEAK_OPENERS = [
    "in today's", "in the modern", "in the current", "in this day and age",
    "it is important", "it is crucial", "it is essential",
    "as we all know", "needless to say", "it goes without saying",
    "have you ever", "are you looking", "do you want",
]


# ---------------------------------------------------------------------------
# Individual checks — each returns Optional[ValidationFailure]
#   None  → check passed
#   obj   → issue found (severity + message + suggestion)
# ---------------------------------------------------------------------------

CheckFn = Callable[[str, dict], Optional[ValidationFailure]]
_REGISTRY: dict[str, CheckFn] = {}


def _check(name: str):
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[name] = fn
        return fn
    return decorator


@_check("ai_cliches")
def _ai_cliches(content: str, ctx: dict) -> Optional[ValidationFailure]:
    content_lower = content.lower()
    found = [p for p in AI_CLICHES if p in content_lower]
    if not found:
        return None
    return ValidationFailure(
        check="ai_cliches",
        severity="high",
        message=f"AI clichés detected ({len(found)}): {', '.join(repr(p) for p in found[:5])}",
        suggestion="Replace each cliché with the specific thing it was hiding. 'leverage' → name the specific mechanism. 'game-changer' → name the specific change.",
    )


@_check("generic_phrases")
def _generic_phrases(content: str, ctx: dict) -> Optional[ValidationFailure]:
    content_lower = content.lower()
    found = [p for p in GENERIC_PHRASES if p in content_lower]
    if not found:
        return None
    return ValidationFailure(
        check="generic_phrases",
        severity="medium",
        message=f"Generic phrasing detected: {', '.join(repr(p) for p in found[:3])}",
        suggestion="Replace with a specific claim that could only apply to this topic.",
    )


@_check("weak_opener")
def _weak_opener(content: str, ctx: dict) -> Optional[ValidationFailure]:
    first_line = content.strip().split("\n")[0].strip().lower()
    for opener in _WEAK_OPENERS:
        if first_line.startswith(opener):
            return ValidationFailure(
                check="weak_opener",
                severity="high",
                message=f"Weak opener: starts with '{first_line[:60]}...'",
                suggestion="Rewrite the first line with a specific claim, surprising insight, or a direct statement of the core tension.",
            )
    return None


@_check("fake_statistics")
def _fake_statistics(content: str, ctx: dict) -> Optional[ValidationFailure]:
    content_lower = content.lower()
    found = [p for p in FAKE_STAT_PATTERNS if p in content_lower]
    if not found:
        return None
    return ValidationFailure(
        check="fake_statistics",
        severity="high",
        message=f"Unattributed statistic language detected: {', '.join(repr(p) for p in found[:3])}",
        suggestion="Remove unsupported claims or replace with a specific, sourced statistic. If you don't have the data, don't cite 'studies'.",
    )


@_check("sentence_length")
def _sentence_length(content: str, ctx: dict) -> Optional[ValidationFailure]:
    cleaned = re.sub(r"[!?]", ".", content)
    sentences = [s.strip() for s in cleaned.split(".") if s.strip() and len(s.split()) > 2]
    if not sentences:
        return None
    avg = sum(len(s.split()) for s in sentences) / len(sentences)
    if avg <= 22:
        return None
    return ValidationFailure(
        check="sentence_length",
        severity="medium",
        message=f"Average sentence length is {avg:.0f} words (threshold: 22). Content reads as dense.",
        suggestion="Break long sentences in two. Short sentences create emphasis. Vary rhythm deliberately.",
    )


@_check("repetition")
def _repetition(content: str, ctx: dict) -> Optional[ValidationFailure]:
    words = content.lower().split()
    phrase_counts: dict[str, int] = {}
    for i in range(len(words) - 2):
        phrase = " ".join(words[i: i + 3])
        if len(phrase) > 10:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
    repeated = [p for p, c in phrase_counts.items() if c >= 3]
    if not repeated:
        return None
    return ValidationFailure(
        check="repetition",
        severity="medium",
        message=f"Repeated phrases detected ({len(repeated)}): '{repeated[0]}'",
        suggestion="Vary phrasing — repetition signals padding. Rephrase or cut the repeated instances.",
    )


@_check("exclamations")
def _exclamations(content: str, ctx: dict) -> Optional[ValidationFailure]:
    count = content.count("!")
    excess = max(0, count - 2)
    if excess == 0:
        return None
    return ValidationFailure(
        check="exclamations",
        severity="low",
        message=f"Excessive exclamation marks: {count} found (max 2 recommended).",
        suggestion="Remove exclamation marks. Earned punctuation is not needed when the content creates the energy.",
    )


@_check("cta_quality")
def _cta_quality(content: str, ctx: dict) -> Optional[ValidationFailure]:
    platform = ctx.get("platform", {})
    requires_cta = platform.get("validation", {}).get("requires_cta", False)

    if not requires_cta:
        return None

    content_lower = content.lower()
    last_quarter = content_lower[-max(len(content_lower) // 4, 200):]

    # Check for weak CTA
    for signal in _WEAK_CTA_SIGNALS:
        if signal in content_lower:
            return ValidationFailure(
                check="cta_quality",
                severity="high",
                message=f"Weak CTA detected: '{signal}'",
                suggestion="Replace with a specific question your audience has a real opinion on, or a single concrete action with minimum friction.",
            )

    # Check for any CTA
    has_question = "?" in last_quarter
    has_action = any(
        word in last_quarter
        for word in ["share", "comment", "reply", "connect", "try", "book",
                     "schedule", "follow", "save", "dm", "reach out", "tell me"]
    )

    if not has_question and not has_action:
        return ValidationFailure(
            check="cta_quality",
            severity="high",
            message="No clear call-to-action detected.",
            suggestion="End with a specific question your audience has a real opinion on, or one clear, low-friction action.",
        )

    return None


@_check("hashtag_count")
def _hashtag_count(content: str, ctx: dict) -> Optional[ValidationFailure]:
    platform = ctx.get("platform", {})
    hashtag_rule = platform.get("validation", {}).get("hashtag_count", {})

    if not hashtag_rule:
        return None

    min_h = hashtag_rule.get("min", 0)
    max_h = hashtag_rule.get("max", 99)

    if min_h == 0 and max_h == 0:
        # No hashtags allowed
        found = re.findall(r"#\w+", content)
        if found:
            return ValidationFailure(
                check="hashtag_count",
                severity="medium",
                message=f"Hashtags not appropriate for this platform ({len(found)} found).",
                suggestion=f"Remove all hashtags for {platform.get('label', 'this platform')}.",
            )
        return None

    found = re.findall(r"#\w+", content)
    count = len(found)

    if not (min_h <= count <= max_h):
        return ValidationFailure(
            check="hashtag_count",
            severity="high",
            message=f"Hashtag count: {count} found, expected {min_h}-{max_h}.",
            suggestion=f"Use exactly {min_h} to {max_h} hashtags, placed at the very end of the content.",
        )

    # Check positioning (should be at the end for LinkedIn)
    if min_h > 0:
        content_no_tags = re.sub(r"\s*#\w+", "", content).strip()
        last_200 = content[-200:]
        inline_tags = [t for t in found if t in content_no_tags]
        if inline_tags:
            return ValidationFailure(
                check="hashtag_count",
                severity="medium",
                message=f"Hashtags found inline — they should be grouped at the end.",
                suggestion="Move all hashtags to the final line of the content.",
            )

    return None


@_check("content_length")
def _content_length(content: str, ctx: dict) -> Optional[ValidationFailure]:
    platform = ctx.get("platform", {})
    max_words = platform.get("validation", {}).get("max_words")

    if not max_words:
        return None

    word_count = len(content.split())
    if word_count <= max_words:
        return None

    return ValidationFailure(
        check="content_length",
        severity="medium",
        message=f"Content is {word_count} words — exceeds platform limit of {max_words}.",
        suggestion=f"Trim to under {max_words} words. Cut the weakest paragraph first.",
    )


@_check("title_presence")
def _title_presence(content: str, ctx: dict) -> Optional[ValidationFailure]:
    platform = ctx.get("platform", {})
    requires_title = platform.get("validation", {}).get("requires_title", False)

    if not requires_title:
        return None

    first_line = content.strip().split("\n")[0].strip()
    has_title = first_line.startswith("#") or (len(first_line) < 80 and not first_line.endswith("."))

    if not has_title:
        return ValidationFailure(
            check="title_presence",
            severity="high",
            message="Missing title or heading at the start.",
            suggestion="Add a clear, specific title as the first line. Use markdown heading (#) for blog/SEO content.",
        )

    return None


@_check("paragraph_length")
def _paragraph_length(content: str, ctx: dict) -> Optional[ValidationFailure]:
    platform = ctx.get("platform", {})
    max_para_words = platform.get("validation", {}).get("max_para_words")

    if not max_para_words:
        return None

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    long_paras = [p for p in paragraphs if len(p.split()) > max_para_words]

    if not long_paras:
        return None

    return ValidationFailure(
        check="paragraph_length",
        severity="medium",
        message=f"{len(long_paras)} paragraph(s) exceed the platform word limit ({max_para_words} words/paragraph).",
        suggestion="Break long paragraphs in two. Short paragraphs improve readability and platform engagement.",
    )


@_check("passive_voice")
def _passive_voice(content: str, ctx: dict) -> Optional[ValidationFailure]:
    matches = _PASSIVE_RE.findall(content)
    if len(matches) < 3:
        return None
    return ValidationFailure(
        check="passive_voice",
        severity="low",
        message=f"Multiple passive voice constructions found ({len(matches)}).",
        suggestion="Rewrite in active voice. Instead of 'was built by the team', use 'the team built it'.",
    )


# ---------------------------------------------------------------------------
# Main validation function
# ---------------------------------------------------------------------------

def validate(content: str, ctx: dict) -> ValidationResult:
    """
    Run all validation checks and return a structured result.

    Args:
        content: The generated content to validate.
        ctx:     Context dict with 'platform', 'audience', 'tone'.

    Returns:
        ValidationResult with score, grade, failures, and warnings.
    """
    if not content.strip():
        return ValidationResult(
            score=0, grade="poor",
            passed=[],
            failures=[ValidationFailure(
                check="content_empty", severity="critical",
                message="Content is empty.", suggestion="Generate content first.",
            )],
            warnings=[],
            summary="No content to evaluate.",
        )

    failures: list[ValidationFailure] = []
    warnings:  list[ValidationFailure] = []
    passed:    list[str] = []
    score = 100

    _score_map = {
        "ai_cliches":      _W["ai_cliche"],
        "generic_phrases": _W["generic"],
        "weak_opener":     _W["weak_opener"],
        "fake_statistics": _W["fake_stat"],
        "sentence_length": _W["long_sentences"],
        "repetition":      _W["repetition"],
        "exclamations":    _W["exclamations"],
        "cta_quality":     _W["no_cta"],
        "hashtag_count":   _W["hashtag_wrong"],
        "content_length":  _W["too_long"],
        "title_presence":  _W["no_title"],
        "paragraph_length": _W["long_paragraphs"],
        "passive_voice":   _W["passive_voice"],
    }

    for name, check_fn in _REGISTRY.items():
        result = check_fn(content, ctx)
        if result is None:
            passed.append(name)
        elif result.severity in ("critical", "high"):
            failures.append(result)
            score = max(0, score - _score_map.get(name, 5))
        else:
            warnings.append(result)
            score = max(0, score - max(2, _score_map.get(name, 3) // 2))

    score = max(0, min(100, score))

    if score >= 90:
        grade = "excellent"
        summary = "Content is ready — minor polish only if needed."
    elif score >= 75:
        grade = "good"
        summary = "Acceptable quality — consider strengthening the hook or CTA."
    elif score >= 55:
        grade = "fair"
        summary = "Noticeable issues — repair recommended before publishing."
    else:
        grade = "poor"
        summary = "Major quality problems — content reads as generic or AI-generated."

    return ValidationResult(
        score=score,
        grade=grade,
        passed=passed,
        failures=failures,
        warnings=warnings,
        summary=summary,
    )
