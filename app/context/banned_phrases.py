"""
Banned Phrase Registry — single source of truth.

Centralizes all banned phrases that previously lived in:
  - app/knowledge/examples/content_examples.py (AI_CLICHES)
  - app/services/style_entropy.py (BANNED_TRANSITIONS)
  - app/services/human_validator.py (_GENERIC_PATTERNS, _ROBOTIC_TRANSITIONS)
  - app/agents/validator.py (_WEAK_CTA_SIGNALS)

Used in three places:
  1. Context injection  — tell the LLM what not to write
  2. Pre-generation scan — flag banned phrases in the user's topic
  3. Post-generation scoring — penalize detected phrases in output
"""

import random
import re

# ---------------------------------------------------------------------------
# Universal — banned in every context
# ---------------------------------------------------------------------------

UNIVERSAL_BANNED: list[str] = [
    # AI authorship signals
    "leverage", "leveraging", "leveraged",
    "game-changer", "game changer",
    "groundbreaking", "revolutionary", "transformative",
    "synergy", "synergize",
    "paradigm shift",
    "thought leader", "thought leadership",
    "deep dive",
    "unpack",
    "unlock",
    "empower", "empowering",
    "seamless", "seamlessly",
    "robust solution",
    "holistic approach",
    "best-in-class", "world-class",
    "value proposition",
    "moving the needle",
    "scalable solution",
    "driving results",
    "circle back",
    "ecosystem",
    "disruptive", "disruption",
    # Robotic openers
    "in today's world",
    "in today's fast-paced",
    "in the modern",
    "in this day and age",
    "as we all know",
    "needless to say",
    "it goes without saying",
    "it is important to note",
    "it's important to note",
    "it is worth mentioning",
    "it is crucial to",
    "it is essential to",
    # Robotic transitions
    "here's why that matters",
    "here's the thing",
    "the reality is",
    "the truth is",
    "simply put",
    "in other words",
    "to be clear",
    "the bottom line is",
    "let me explain",
    "that being said",
    "having said that",
    "first and foremost",
    "last but not least",
    "in a nutshell",
    "all things considered",
    "at the end of the day",
    "when it comes to",
    # Fake authority
    "studies show",
    "research shows",
    "experts say",
    "according to experts",
    "it has been proven",
    "statistics show",
    # Vague padding
    "obviously",
    "of course",
    "as mentioned",
    "needless to say",
]

# ---------------------------------------------------------------------------
# Platform-specific additions
# ---------------------------------------------------------------------------

PLATFORM_BANNED: dict[str, list[str]] = {
    "linkedin_post": [
        "like and share",
        "follow for more",
        "subscribe for more",
        "hope this helps",
        "let me know your thoughts",
        "drop a comment below",
        "feel free to reach out",
        "don't hesitate to contact",
        "looking forward to hearing from you",
        "share if you agree",
    ],
    "cold_email": [
        "just wanted to",
        "hope this email finds you well",
        "I hope you're doing well",
        "touching base",
        "circling back",
        "as per my previous email",
        "per our last conversation",
        "partnership opportunity",
        "mutual benefit",
        "I wanted to reach out because",
        "I came across your profile",
    ],
    "blog": [
        "in conclusion",
        "to summarize",
        "as you can see",
        "in this article we will",
        "in this blog post we will",
        "stay tuned",
        "in this post",
    ],
    "ad_copy": [
        "click here",
        "learn more",
        "find out more",
        "amazing",
        "incredible",
        "once in a lifetime",
        "act now",
        "don't miss out",
        "limited time offer",
    ],
    "seo_article": [
        "in this comprehensive guide",
        "everything you need to know",
        "the ultimate guide",
        "in this article we will cover",
    ],
}

# ---------------------------------------------------------------------------
# Audience-specific additions
# ---------------------------------------------------------------------------

AUDIENCE_BANNED: dict[str, list[str]] = {
    "ai_engineer": [
        "artificial intelligence",  # too generic for expert audience
        "AI-powered",
        "cutting-edge AI",
        "state-of-the-art",
        "next-generation",
        "smart AI",
    ],
    "startup_founder": [
        "fail fast",
        "move fast and break things",
        "hustle",
        "10x your",
        "crushing it",
        "killing it",
        "grind",
        "growth hacking",
    ],
    "enterprise_buyer": [
        "cheap",
        "affordable",
        "budget-friendly",
        "quick fix",
        "hack",
        "workaround",
        "startup-style",
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_banned(
    platform_id: str = "",
    audience_id: str = "",
    include_universal: bool = True,
) -> list[str]:
    """Return the full banned phrase list for the given context."""
    result: list[str] = []
    if include_universal:
        result.extend(UNIVERSAL_BANNED)
    if platform_id:
        result.extend(PLATFORM_BANNED.get(platform_id, []))
    if audience_id:
        result.extend(AUDIENCE_BANNED.get(audience_id, []))
    return list(dict.fromkeys(result))  # deduplicate, preserve order


def validate_content(
    content: str,
    platform_id: str = "",
    audience_id: str = "",
) -> list[str]:
    """
    Scan content for banned phrases.

    Returns list of detected phrases (empty = clean).
    Used for pre-generation topic scanning and post-generation quality audit.
    """
    banned = get_banned(platform_id, audience_id)
    content_lower = content.lower()
    return [p for p in banned if p.lower() in content_lower]


def format_for_prompt(
    platform_id: str = "",
    audience_id: str = "",
    n: int = 14,
) -> str:
    """
    Format a random sample of the banned list for prompt injection.

    Sampling per call creates variation — the LLM sees different examples
    each request rather than the same list memorized as a template.
    """
    banned = get_banned(platform_id, audience_id)
    sample = random.sample(banned, min(n, len(banned)))
    lines = ["Never use any of these phrases — they signal AI authorship:"]
    for p in sample:
        lines.append(f'  [BANNED] "{p}"')
    return "\n".join(lines)
