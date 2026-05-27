"""
Content Memory — Lightweight in-process generation history.

Tracks structural patterns (hook type, transitions, CTA shape) used across
recent generations to prevent repetitive outputs in the same session.

Design:
  - Module-level singleton — shared across all requests in the process.
  - Thread-safe via Lock.
  - Not persisted across restarts: suitable for single-instance deployments.
    For multi-instance, swap the deques for Redis lists.

Usage:
  content_memory.register(final_output, use_case)   # after each generation
  content_memory.get_variety_directive(use_case)     # before next prompt build
"""

import re
from collections import deque
from threading import Lock

# ---------------------------------------------------------------------------
# Pattern detectors
# ---------------------------------------------------------------------------

_HOOK_PATTERNS: list[tuple[str, str]] = [
    (r"^(most|many|few|all|some|every)\b",     "quantifier-opener"),
    (r"^(here'?s|there'?s)\b",                 "heres-opener"),
    (r"^(the biggest|the hardest|the real|the problem|the truth|the key)\b", "the-X-opener"),
    (r"^(i (built|shipped|learned|discovered|made|realized))\b",   "i-verb-opener"),
    (r"^(we (built|shipped|learned|discovered|made|realized))\b",  "we-verb-opener"),
    (r"^(stop|don'?t|never|always)\b",         "imperative-opener"),
    (r"^\d+\s+\w",                             "number-opener"),
    (r"^in \d+",                               "in-number-opener"),
    (r"^if you\b",                             "if-you-opener"),
    (r"^(what|why|how)\b",                     "question-opener"),
]

_TRANSITION_DETECTORS: list[str] = [
    "here's why",
    "the reality is",
    "the truth is",
    "to be clear",
    "simply put",
    "in other words",
    "the bottom line",
    "at the end of the day",
    "that being said",
    "having said that",
    "first and foremost",
    "here's the thing",
    "as we all know",
    "needless to say",
    "long story short",
    "in a nutshell",
]

_CTA_PATTERNS: list[tuple[str, str]] = [
    (r"what'?s your (take|thought|experience|view)", "whats-your-take"),
    (r"(drop|leave|share) (a|your) (comment|thought|take)",  "drop-comment"),
    (r"(agree|disagree)\?",                                  "agree-disagree"),
    (r"(let me know|tell me) (what|how|if|your)",            "let-me-know"),
    (r"(have you|did you|are you) (ever|tried|seen|experienced)", "have-you-ever"),
    (r"follow (me|us) for",                                  "follow-for-more"),
    (r"(like|save) (this|if)",                               "like-save"),
    (r"(dm|message|reach out)",                              "dm-cta"),
]


def _classify_hook(first_line: str) -> str:
    line = first_line.lower().strip()
    for pattern, label in _HOOK_PATTERNS:
        if re.search(pattern, line):
            return label
    return "other"


def _detect_transitions(content: str) -> list[str]:
    found = []
    content_lower = content.lower()
    for phrase in _TRANSITION_DETECTORS:
        if phrase in content_lower:
            found.append(phrase)
    return found


def _classify_cta(last_300: str) -> str:
    text = last_300.lower()
    for pattern, label in _CTA_PATTERNS:
        if re.search(pattern, text):
            return label
    return "other"


def _extract_first_line(content: str) -> str:
    for line in content.strip().split("\n"):
        line = line.strip()
        if len(line) > 10 and not line.startswith("#"):
            return line
    return content[:120]


# ---------------------------------------------------------------------------
# Memory store
# ---------------------------------------------------------------------------

class ContentMemory:
    def __init__(self, max_history: int = 50):
        self._hook_labels:   deque[str] = deque(maxlen=max_history)
        self._transitions:   deque[str] = deque(maxlen=max_history * 6)
        self._cta_labels:    deque[str] = deque(maxlen=max_history)
        self._lock = Lock()

    # ------------------------------------------------------------------

    def register(self, content: str, use_case: str = "") -> None:
        """
        Record structural patterns from a generated output.
        Call this after the pipeline finalizes content.
        """
        first_line  = _extract_first_line(content)
        hook_label  = _classify_hook(first_line)
        transitions = _detect_transitions(content)
        cta_label   = _classify_cta(content[-300:])

        with self._lock:
            self._hook_labels.append(hook_label)
            self._cta_labels.append(cta_label)
            for t in transitions:
                self._transitions.append(t)

    # ------------------------------------------------------------------

    def check_repetition(self) -> dict:
        """
        Return structural patterns that have been overused recently.
        """
        with self._lock:
            hook_counts: dict[str, int] = {}
            for h in self._hook_labels:
                hook_counts[h] = hook_counts.get(h, 0) + 1

            transition_counts: dict[str, int] = {}
            for t in self._transitions:
                transition_counts[t] = transition_counts.get(t, 0) + 1

            cta_counts: dict[str, int] = {}
            for c in self._cta_labels:
                cta_counts[c] = cta_counts.get(c, 0) + 1

            overused_hooks = [
                k for k, v in hook_counts.items() if v >= 3 and k != "other"
            ]
            overused_transitions = [
                k for k, v in transition_counts.items() if v >= 2
            ]
            overused_ctas = [
                k for k, v in cta_counts.items() if v >= 3 and k != "other"
            ]

            return {
                "overused_hooks":       overused_hooks,
                "overused_transitions": overused_transitions,
                "overused_ctas":        overused_ctas,
                "history_size":         len(self._hook_labels),
            }

    def get_variety_directive(self, use_case: str = "") -> str:
        """
        Return a prompt directive to avoid recently overused patterns.
        Returns empty string if history is too small to be meaningful.
        """
        with self._lock:
            history_size = len(self._hook_labels)

        if history_size < 5:
            return ""

        rep = self.check_repetition()
        parts: list[str] = []

        if rep["overused_hooks"]:
            label_str = ", ".join(repr(h) for h in rep["overused_hooks"][:3])
            parts.append(
                f"Recent outputs have repeated these opening patterns — avoid them: {label_str}. "
                "Use a structurally different type of opening."
            )

        if rep["overused_transitions"]:
            phrase_str = ", ".join(f'"{t}"' for t in rep["overused_transitions"][:3])
            parts.append(
                f"These transition phrases have appeared in too many recent outputs: {phrase_str}. "
                "Use different connective language or no transition at all."
            )

        if rep["overused_ctas"]:
            parts.append(
                "The closing CTA pattern has been repeated across recent generations. "
                "Use a different ending approach: a direct question, an action, or an abrupt stop."
            )

        return "\n".join(parts)

    def reset(self) -> None:
        """Clear all stored history. Primarily for testing."""
        with self._lock:
            self._hook_labels.clear()
            self._transitions.clear()
            self._cta_labels.clear()


# ---------------------------------------------------------------------------
# Module-level singleton — used by the workflow
# ---------------------------------------------------------------------------

_memory = ContentMemory(max_history=50)


def register(content: str, use_case: str = "") -> None:
    _memory.register(content, use_case)


def get_variety_directive(use_case: str = "") -> str:
    return _memory.get_variety_directive(use_case)


def check_repetition() -> dict:
    return _memory.check_repetition()


def reset() -> None:
    _memory.reset()
