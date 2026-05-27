"""
Humanization Validator — Pipeline Stage 6b

Scores content on four dimensions of human authenticity.
No LLM calls — all checks are heuristic and deterministic.
Reproducible, fast, and stackable with the quality validator.

Score 0-100 (sum of four 0-25 subscores):
  80-100 → Human   — reads like a practitioner wrote it
  60-79  → Borderline — structurally fine, detectable AI rhythm
  0-59   → Robotic  — template-like, generic, experientially hollow
"""

import re
from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Signal patterns
# ---------------------------------------------------------------------------

# Presence of these patterns raises the specificity score
_SPECIFICITY_PATTERNS: list[str] = [
    r"\b\d+\s*(ms|milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?)\b",
    r"\b\d+(\.\d+)?%\b",
    r"\b\d+x\b",
    r"\b\$\d[\d,]*",
    r"\bgpt-[34]",
    r"\bllama[-\s]?\d",
    r"\bclaude[-\s]?(3|sonnet|haiku|opus)?",
    r"\bgemini\b",
    r"\bopenai\b",
    r"\banthrop",
    r"\breact|vue|svelte|angular|next\.?js\b",
    r"\bpostgres|mysql|redis|mongo|elastic",
    r"\bkubernetes|docker|terraform",
    r"\baws|gcp|azure\b",
    r"\bpython|typescript|golang|rust\b",
    r"\b(q[1-4]|january|february|march|april|may|june|july|august|september|october|november|december)\s+20\d\d\b",
    r"\bweek \d+\b",
    r"\b\d+ (engineers?|developers?|users?|customers?|requests?|tokens?)\b",
]

# Presence of these patterns raises the tension/narrative score
_TENSION_PATTERNS: list[str] = [
    r"\b(failed|failure|broke|crashed|panicked|went wrong|error|incident|bug)\b",
    r"\b(but|however|except|until|unless|despite|though|although|yet)\b",
    r"\b(surprised|unexpected|counterintuitive|shocked|didn't expect|turned out)\b",
    r"\b(tradeoff|trade-off|constraint|bottleneck|edge case|postmortem)\b",
    r"\bwe (learned|realized|discovered|found out|noticed|eventually)\b",
    r"\bthe problem was\b",
    r"\bwhat we missed\b",
    r"\bit took (us|me|the team)\b",
    r"\bregret|wrong decision|mistake|should have\b",
]

# Generic/AI phrases that penalize originality
_GENERIC_PATTERNS: list[str] = [
    r"\bin today'?s (world|fast.paced|competitive|digital|rapidly evolving)\b",
    r"\bit is (important|crucial|essential|critical|vital) to\b",
    r"\bleverage\b",
    r"\bgame.changer\b",
    r"\bsynergy\b",
    r"\bparadigm shift\b",
    r"\bthought leader",
    r"\bmoving the needle\b",
    r"\bscalable solution\b",
    r"\bvalue proposition\b",
    r"\bbest.in.class\b",
    r"\bworld.class\b",
    r"\bseamless(ly)?\b",
    r"\bholistic approach\b",
    r"\bdriving results\b",
    r"\bempower\b",
    r"\brobust solution\b",
    r"\bpivot\b",
    r"\bdeep dive\b",
    r"\bunpack\b",
    r"\bunlock\b",
    r"\blandscape\b",
    r"\bechosystem\b",
]

# Robotic structural transitions that penalize originality
_ROBOTIC_TRANSITIONS: list[str] = [
    r"here'?s why that matters",
    r"the reality is",
    r"the truth is",
    r"it'?s important to note",
    r"simply put,?",
    r"in other words,?",
    r"to be clear,?",
    r"the bottom line is",
    r"let me explain",
    r"here'?s the thing",
    r"at the end of the day",
    r"as we all know",
    r"needless to say",
    r"that being said",
    r"having said that",
    r"first and foremost",
    r"last but not least",
    r"in a nutshell",
    r"all things considered",
    r"long story short",
    r"believe it or not",
    r"more often than not",
]

# Signals that content comes from lived experience
_EXPERIENCE_PATTERNS: list[str] = [
    r"\b(we|i|our team|my team)\s+(shipped|built|deployed|launched|discovered|noticed|realized|learned)\b",
    r"\b(in production|in staging|at production scale|in the wild)\b",
    r"\b(three months|six months|two years|last quarter|this quarter|in week \d+)\b",
    r"\bturned out\b",
    r"\bwe (thought|assumed|expected|estimated).{5,50}but\b",
    r"\b(measured|profiled|benchmarked|traced|monitored|instrumented)\b",
    r"\b(incident|postmortem|on-call|pager|alert|runbook)\b",
    r"\bwe (had to|ended up|decided to|chose to)\b",
    r"\bmy (first|biggest|worst|best) mistake\b",
    r"\bthe (decision|tradeoff|call|choice) was\b",
]

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class HumanizationResult:
    score: int
    grade: Literal["human", "borderline", "robotic"]
    specificity_score: int   # 0-25
    tension_score: int       # 0-25
    originality_score: int   # 0-25
    experience_score: int    # 0-25
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "score":             self.score,
            "grade":             self.grade,
            "specificity_score": self.specificity_score,
            "tension_score":     self.tension_score,
            "originality_score": self.originality_score,
            "experience_score":  self.experience_score,
            "issues":            self.issues,
            "suggestions":       self.suggestions,
        }


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def _count(text: str, patterns: list[str]) -> int:
    count = 0
    text_lower = text.lower()
    for p in patterns:
        count += len(re.findall(p, text_lower))
    return count


def _word_count(content: str) -> int:
    return max(len(content.split()), 1)


def _score_specificity(content: str) -> tuple[int, list[str], list[str]]:
    """0-25: concrete numbers, tool names, timeframes, proper nouns."""
    hits = _count(content, _SPECIFICITY_PATTERNS)
    density = hits / (_word_count(content) / 100)

    issues: list[str] = []
    suggestions: list[str] = []

    if density < 0.5:
        score = max(0, int(density * 30))
        issues.append("Low specificity: no concrete numbers, tool names, or timeframes detected")
        suggestions.append("Add at least one specific number, named technology, or timeline.")
    elif density < 1.5:
        score = min(20, int(10 + density * 6))
    else:
        score = min(25, int(density * 10))

    return score, issues, suggestions


def _score_tension(content: str) -> tuple[int, list[str], list[str]]:
    """0-25: conflict, failure, counterintuitive outcomes, narrative reversals."""
    hits = _count(content, _TENSION_PATTERNS)
    density = hits / (_word_count(content) / 100)

    issues: list[str] = []
    suggestions: list[str] = []

    if density < 1.0:
        score = max(0, int(density * 15))
        issues.append("No narrative tension: content reads as declarative without conflict or reversal")
        suggestions.append("Include something that failed, surprised you, or contradicted expectations.")
    elif density < 3.0:
        score = min(22, int(12 + density * 4))
    else:
        score = min(25, int(density * 7))

    return score, issues, suggestions


def _score_originality(content: str) -> tuple[int, list[str], list[str]]:
    """0-25: absence of generic phrases and robotic structural transitions."""
    generic_hits   = _count(content, _GENERIC_PATTERNS)
    robotic_hits   = _count(content, _ROBOTIC_TRANSITIONS)
    words          = _word_count(content)

    total_penalty     = generic_hits * 3 + robotic_hits * 5
    penalty_per_100   = total_penalty / (words / 100)

    issues: list[str] = []
    suggestions: list[str] = []

    if generic_hits > 0:
        issues.append(
            f"Generic language detected ({generic_hits} instances): "
            "clichéd phrases erode perceived authorship"
        )
    if robotic_hits > 0:
        issues.append(
            f"Robotic transitions detected ({robotic_hits} instances): "
            "structural filler phrases that mark AI-generated text"
        )
    if generic_hits > 0 or robotic_hits > 0:
        suggestions.append("Remove generic transitions and replace clichés with what was specifically meant.")

    score = max(0, 25 - int(penalty_per_100 * 5))
    return score, issues, suggestions


def _score_experience(content: str) -> tuple[int, list[str], list[str]]:
    """0-25: signals that the author has done the thing — not just read about it."""
    hits    = _count(content, _EXPERIENCE_PATTERNS)
    density = hits / (_word_count(content) / 100)

    issues: list[str] = []
    suggestions: list[str] = []

    if density < 0.5:
        score = max(0, int(density * 25))
        issues.append("Low experiential realism: reads as conceptual rather than practitioner-derived")
        suggestions.append(
            "Ground the content in a specific decision, failure, or production observation "
            "rather than a general principle."
        )
    elif density < 1.5:
        score = min(20, int(10 + density * 7))
    else:
        score = min(25, int(density * 13))

    return score, issues, suggestions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_humanization(content: str) -> HumanizationResult:
    """
    Score content for human authenticity across four dimensions.

    Returns a HumanizationResult with dimension scores and repair suggestions.
    Fast, deterministic, no LLM calls.
    """
    if not content.strip():
        return HumanizationResult(
            score=0, grade="robotic",
            specificity_score=0, tension_score=0,
            originality_score=0, experience_score=0,
            issues=["Empty content"],
        )

    spec_score, spec_issues, spec_sug     = _score_specificity(content)
    tension_score, ten_issues, ten_sug    = _score_tension(content)
    orig_score, orig_issues, orig_sug     = _score_originality(content)
    exp_score, exp_issues, exp_sug        = _score_experience(content)

    total = spec_score + tension_score + orig_score + exp_score

    if total >= 80:
        grade: Literal["human", "borderline", "robotic"] = "human"
    elif total >= 60:
        grade = "borderline"
    else:
        grade = "robotic"

    all_issues      = spec_issues + ten_issues + orig_issues + exp_issues
    all_suggestions = spec_sug + ten_sug + orig_sug + exp_sug

    return HumanizationResult(
        score=total,
        grade=grade,
        specificity_score=spec_score,
        tension_score=tension_score,
        originality_score=orig_score,
        experience_score=exp_score,
        issues=all_issues,
        suggestions=all_suggestions,
    )
