"""
Style Entropy Engine

Prevents AI-template rhythm by injecting per-request variation directives
into the generation prompt. Every call returns a different mix of structural
constraints so the LLM cannot settle into the same groove.

Also maintains the canonical banned-transitions list used across the pipeline.
"""

import random

# ---------------------------------------------------------------------------
# Banned transitions — the most common markers of AI-generated structure
# ---------------------------------------------------------------------------

BANNED_TRANSITIONS: list[str] = [
    "Here's why that matters",
    "Here's the thing",
    "Here's what I mean",
    "Here's the reality",
    "The reality is",
    "The truth is",
    "The fact of the matter is",
    "It's important to note",
    "It is important to",
    "It's worth mentioning",
    "It's worth noting",
    "Needless to say",
    "Simply put",
    "In other words",
    "To be clear",
    "What this means is",
    "The bottom line is",
    "Let me explain",
    "At the end of the day",
    "It goes without saying",
    "As we all know",
    "When it comes to",
    "More often than not",
    "Believe it or not",
    "Long story short",
    "That being said",
    "Having said that",
    "With that being said",
    "First and foremost",
    "Last but not least",
    "All things considered",
    "In a nutshell",
    "In today's world",
    "In today's fast-paced",
    "In the modern",
    "In this day and age",
]

# ---------------------------------------------------------------------------
# Directive pools — sampled randomly each call
# ---------------------------------------------------------------------------

_RHYTHM_POOL: list[str] = [
    "No two consecutive paragraphs should start with the same word or structural pattern.",
    "Your longest sentence must follow your shortest. Contrast controls reading pace.",
    "Write at least one sentence under 8 words. Write at least one sentence over 25 words.",
    "Let one paragraph be a single sentence — no explanation, no follow-up. It stands alone.",
    "Use a one-sentence paragraph at least once. Not for decoration — for impact.",
    "The first and last sentences of the piece must be the two shortest.",
    "Start no more than two sentences with 'The'. Use 'This', 'That', 'It', or cut the article.",
    "Every third paragraph should be notably shorter than the two before it.",
    "Use at least one sentence fragment for emphasis. Fragments create rhythm breaks.",
]

_PACING_POOL: list[str] = [
    "Do not use a three-part list unless each item is genuinely different in kind, not degree.",
    "If you use a list, break its rhythm with one standalone sentence after the second item.",
    "Avoid smooth transitions. Abrupt paragraph breaks create emphasis — use them deliberately.",
    "End the piece before the reader expects you to. The exit is an editorial decision.",
    "The second paragraph should be the most compressed idea — not an expansion of the first.",
    "No paragraph should contain both a claim and its full explanation. Split them.",
    "Create one moment of intentional asymmetry: a very short point amid longer development.",
]

_OPENER_POOL: list[str] = [
    "Start with a specific number, a named tool, or a named person — not a concept.",
    "Start mid-thought. Skip the setup. The reader will catch up.",
    "Start with the thing that went wrong. Not what was supposed to happen — what did.",
    "Start with a constraint: 'We had 48 hours and one engineer.' Not the backstory.",
    "Start with a question the reader has but hasn't said out loud. Don't announce you're answering it.",
    "Start with a single declarative sentence that sounds wrong to most practitioners in this field.",
    "Start with the conclusion. Let the piece be the argument for why it's true.",
    "Start with a specific failure. Not a category of failure — the specific thing that broke.",
]

_SPECIFICITY_POOL: list[str] = [
    "At least one claim must include a specific number. Not a range — a single number.",
    "Name a tool, a framework, or a product at least once. Not the category — the specific thing.",
    "Include one failure. Not what could go wrong — what actually did.",
    "Reference a timeline: a week, a sprint, '72 hours'. Vague timeframes lose credibility.",
    "Include one thing that surprised you. Not what anyone predicted — what actually happened.",
    "At least one sentence should describe a specific action someone took, not a principle they followed.",
    "Include one piece of information that a non-practitioner would not know to include.",
]

_VOICE_POOL: list[str] = [
    "Use 'we' or 'I' at least once. This is an observation, not a policy document.",
    "Avoid passive voice in the first paragraph entirely — own the agency.",
    "One observation should be stated as an opinion, not as a fact. Use 'I think' or 'In my experience'.",
    "Write one sentence that sounds like it cost something to say — a real admission or a committed position.",
    "Avoid hedging words in the hook: 'might', 'could', 'perhaps', 'arguably' have no place in the opening.",
]


def get_entropy_directives(
    n_rhythm: int = 2,
    n_pacing: int = 1,
    n_opener: int = 1,
    n_specificity: int = 2,
    n_voice: int = 1,
) -> dict[str, list[str]]:
    """
    Return a per-request mix of entropy directives.

    Randomly sampled so no two calls receive identical constraint sets.
    """
    return {
        "rhythm":      random.sample(_RHYTHM_POOL, min(n_rhythm, len(_RHYTHM_POOL))),
        "pacing":      random.sample(_PACING_POOL, min(n_pacing, len(_PACING_POOL))),
        "opener":      random.sample(_OPENER_POOL, min(n_opener, len(_OPENER_POOL))),
        "specificity": random.sample(_SPECIFICITY_POOL, min(n_specificity, len(_SPECIFICITY_POOL))),
        "voice":       random.sample(_VOICE_POOL, min(n_voice, len(_VOICE_POOL))),
    }


def format_entropy_for_prompt(directives: dict[str, list[str]]) -> str:
    """Format entropy directives as a structured prompt block."""
    lines: list[str] = []

    label_map = {
        "opener":      "Opening constraint",
        "rhythm":      "Rhythm rules",
        "pacing":      "Pacing rule",
        "specificity": "Specificity rules",
        "voice":       "Voice rule",
    }

    for key in ["opener", "rhythm", "pacing", "specificity", "voice"]:
        items = directives.get(key, [])
        if not items:
            continue
        label = label_map.get(key, key.title())
        lines.append(f"{label}:")
        for d in items:
            lines.append(f"  → {d}")

    return "\n".join(lines)


def format_banned_transitions_for_prompt(n: int = 16) -> str:
    """
    Return a random sample of banned transitions as a prompt instruction.

    Sampling prevents the list from looking identical every call.
    """
    sample = random.sample(BANNED_TRANSITIONS, min(n, len(BANNED_TRANSITIONS)))
    lines = ["Do not use any of these transitions or opener phrases:"]
    for t in sample:
        lines.append(f'  [BANNED] "{t}"')
    return "\n".join(lines)
