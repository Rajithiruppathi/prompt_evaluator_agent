"""
Stage 1 — Intent Understanding

Detects what the user wants to do:
  create   → write new content from a topic
  improve  → enhance an existing prompt or piece of content
  rewrite  → full rewrite while preserving the core idea
  convert  → change platform or format (e.g. Blog → LinkedIn Post)

Detection priority:
  1. Explicit intent field in request
  2. Signal words in the prompt
  3. Presence of existing_content → improve
  4. Default → create
"""

from typing import Optional

_SIGNALS: dict[str, list[str]] = {
    "create": [
        "write about", "write a", "create a", "generate a", "draft a",
        "write me", "can you write", "help me write", "post about",
        "blog about", "email about",
    ],
    "improve": [
        "improve this", "make this better", "enhance this", "fix this",
        "optimize this", "edit this", "polish this", "refine this",
        "improve my prompt", "make my prompt better", "optimize my prompt",
    ],
    "rewrite": [
        "rewrite this", "rewrite my", "rephrase this", "revamp this",
        "redo this", "reword this", "rework this",
    ],
    "convert": [
        "convert this", "turn this into", "change this to", "make this a",
        "transform this", "adapt this", "convert to", "turn into",
        "reformat this", "change format",
    ],
}


def analyze_intent(
    prompt: str,
    existing_content: Optional[str] = None,
    explicit_intent: Optional[str] = None,
) -> str:
    """
    Determine the content operation intent.
    Returns one of: 'create', 'improve', 'rewrite', 'convert'.
    """
    if explicit_intent and explicit_intent in ("create", "improve", "rewrite", "convert"):
        return explicit_intent

    prompt_lower = prompt.lower()

    for intent, signals in _SIGNALS.items():
        if any(signal in prompt_lower for signal in signals):
            return intent

    if existing_content and existing_content.strip():
        return "improve"

    return "create"


def intent_label(intent: str) -> str:
    labels = {
        "create":  "Creating new content from topic",
        "improve": "Improving existing content",
        "rewrite": "Full rewrite preserving core idea",
        "convert": "Converting to a different format",
    }
    return labels.get(intent, "Creating new content")
