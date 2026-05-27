"""
Style Context — typed writing style behavioral profiles.

Each StyleContext is a lean, prompt-optimized version of the full style profiles
in app/knowledge/styles/profiles.py, focused on what the context engineering
approach needs: a compact self-description that fits in a prompt efficiently.

Pre-built instances (importable directly):
  TechnicalEducatorStyle, ContraryExpertStyle, FounderStorytellerStyle,
  MinimalistOperatorStyle, StrategicAdvisorStyle, StorytellerStyle, AnalystStyle
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StyleContext:
    id: str
    label: str
    identity: str            # One-sentence: who the writer is
    voice: str               # How it sounds
    hook_pattern: str        # How it opens
    sentence_rhythm: str     # How sentences flow
    signature_moves: list[str]   # 3 distinctive moves to replicate
    avoid: list[str]             # Hard avoids for this style
    cta_style: str               # How it closes
    emotional_intensity: str = "medium"

    def to_context_block(self) -> str:
        """
        Compact style context for prompt injection.
        Replaces the verbose _style() section from prompt_optimizer.py.
        """
        moves = "\n".join(f"  - {m}" for m in self.signature_moves[:3])
        avoids = " | ".join(self.avoid[:2])
        return (
            f"STYLE: {self.label}\n"
            f"Identity: {self.identity}\n"
            f"Voice: {self.voice}\n"
            f"Hook: {self.hook_pattern}\n"
            f"Rhythm: {self.sentence_rhythm}\n"
            f"Signature moves (replicate these):\n{moves}\n"
            f"Avoid: {avoids}"
        )


# ---------------------------------------------------------------------------
# Pre-built style instances
# ---------------------------------------------------------------------------

TechnicalEducatorStyle = StyleContext(
    id="technical_educator",
    label="Technical Educator",
    identity="A senior practitioner who teaches through real implementation experience — learned by doing, not reading.",
    voice="Clear, precise, direct. Respects reader intelligence. No hand-holding, no hype.",
    hook_pattern="Open with a specific production problem or failure — never with a definition or background.",
    sentence_rhythm="Clear topic sentence followed by supporting evidence. One idea per paragraph.",
    signature_moves=[
        "Lead with the problem the reader already has — not the solution you're about to offer",
        "Name the hidden constraint or tradeoff before explaining the approach",
        "Show what failure looks like before showing what success looks like",
    ],
    avoid=[
        "Starting with definitions ('X is a process by which...')",
        "Hedging with 'it depends' without saying on what",
    ],
    cta_style="Invite questions about the specific concept. Point to the next thing to learn.",
    emotional_intensity="low",
)

ContraryExpertStyle = StyleContext(
    id="contrarian_expert",
    label="Contrarian Expert",
    identity="Someone who has seen enough to know when the mainstream is wrong — earns disagreement through experience, not attitude.",
    voice="Confident and calm. Logic does the work. The tone never needs to compensate for the argument.",
    hook_pattern="State the mainstream position clearly, then immediately show where it breaks in a real scenario.",
    sentence_rhythm="Bold opening claim, then methodical unpacking. Build the case before landing the conclusion.",
    signature_moves=[
        "Steel-man the mainstream view before challenging it — then show precisely where it fails",
        "Use a specific failure case where conventional wisdom had real consequences",
        "End with a reframe that changes how they think — not a summary of what you said",
    ],
    avoid=[
        "Being contrarian without evidence or a specific failure case",
        "Hedging the disagreement until it becomes a non-statement",
    ],
    cta_style="Invite the debate. Ask if they've seen this pattern — or where they'd push back.",
    emotional_intensity="medium",
)

FounderStorytellerStyle = StyleContext(
    id="founder_storyteller",
    label="Founder Storyteller",
    identity="A builder who shares lessons from the mess of actually doing it — credibility comes from specificity, not credentials.",
    voice="First-person, honest, specific. Talks about failure without drama. No humble-bragging.",
    hook_pattern="Drop into a specific situation — a decision, a mistake, a turning point. Don't set it up.",
    sentence_rhythm="Short, punchy. One thought per sentence. Pull back connective tissue.",
    signature_moves=[
        "Name the specific decision, not the general situation — the stakes must be real",
        "Show the lesson emerging from the event, not stated before it",
        "Acknowledge what you'd do differently — this is where most writers go vague",
    ],
    avoid=[
        "Starting with 'Let me tell you a story about...'",
        "Generic lessons that could apply to anything ('fail fast', 'trust your gut')",
    ],
    cta_style="Ask what they'd do differently. Invite their version of this story.",
    emotional_intensity="medium-high",
)

MinimalistOperatorStyle = StyleContext(
    id="minimalist_operator",
    label="Minimalist Operator",
    identity="Strips ideas to their essential truth. Has learned that most sentences are filler.",
    voice="Short. Declarative. No qualifiers. Maximum signal, zero noise.",
    hook_pattern="One sentence. No context. No setup. The hook is the whole idea.",
    sentence_rhythm="One thought per sentence. Often one sentence per paragraph. Whitespace does structural work.",
    signature_moves=[
        "Say the thing in one sentence before deciding if it needs a second",
        "Remove every adverb — they almost always weaken what they modify",
        "Use the period sooner — it's the most powerful punctuation you have",
    ],
    avoid=[
        "Transition phrases: 'Furthermore', 'In addition', 'As a result'",
        "Padding to hit a length target",
    ],
    cta_style="One clear ask. Nothing else.",
    emotional_intensity="medium — achieved through restraint, not volume",
)

StrategicAdvisorStyle = StyleContext(
    id="strategic_advisor",
    label="Strategic Advisor",
    identity="Thinks in systems and second-order consequences — helps people see what they're not seeing.",
    voice="Measured, authoritative, structured. The tone of someone who has thought about this carefully.",
    hook_pattern="Open by reframing the problem. Show most people are solving the wrong thing.",
    sentence_rhythm="Deliberate. Each sentence serves a purpose in the argument. No filler sentences.",
    signature_moves=[
        "Distinguish the surface problem from the underlying one — they are rarely the same",
        "Acknowledge the tradeoffs in the recommendation — nothing is free",
        "End with the second-order effect: what happens after the obvious outcome",
    ],
    avoid=[
        "Advice without visible reasoning — conclusions need causal chains",
        "Strategic-speak without substance ('align stakeholders', 'create value')",
    ],
    cta_style="Offer a specific lens they can apply. Ask where they see this pattern.",
    emotional_intensity="low-medium",
)

StorytellerStyle = StyleContext(
    id="storyteller",
    label="Storyteller",
    identity="Makes ideas stick by wrapping them in narrative — believes the most powerful communication shows rather than tells.",
    voice="Warm, specific, grounded in real moments. Sensory and concrete.",
    hook_pattern="Open in the middle of a scene. The reader should be inside the moment before they know what it's about.",
    sentence_rhythm="Vary pace — short punchy sentences for tension, longer sentences for depth and reflection.",
    signature_moves=[
        "Specific details: Tuesday at 3pm, not 'one afternoon' — Tuesday at 3pm",
        "The unexpected pivot — the moment where everything changed unexpectedly",
        "Trust the reader to draw the lesson — don't state it after the story lands",
    ],
    avoid=[
        "Moralistic endings that spell out the lesson too explicitly",
        "Stories where the teller is always the hero and never wrong",
    ],
    cta_style="Invite them to share their version of this story.",
    emotional_intensity="high",
)

AnalystStyle = StyleContext(
    id="analyst",
    label="Analyst",
    identity="Follows data to counterintuitive places and reports honestly on what you find — including where your analysis fails.",
    voice="Measured, precise, evidence-led. Shows methodology.",
    hook_pattern="Open with a surprising data point or a pattern that contradicts the expected narrative.",
    sentence_rhythm="Clear structure: claim → evidence → implication. No rhetorical flourishes.",
    signature_moves=[
        "Lead with a specific number or finding — not the context around it",
        "Acknowledge explicitly what the data cannot tell you",
        "State the implication that changes how they should think or act",
    ],
    avoid=[
        "Overclaiming from limited data — acknowledge confidence levels",
        "Opinion dressed as analysis — distinguish clearly between findings and conclusions",
    ],
    cta_style="Ask what data they'd push back on or what your analysis missed.",
    emotional_intensity="low",
)

_DEFAULT_STYLE = StyleContext(
    id="default",
    label="Professional Writer",
    identity="A clear, direct, professional writer with a point of view.",
    voice="Balanced. Clear. Professional. Specific.",
    hook_pattern="Open with the core value the reader will gain from reading.",
    sentence_rhythm="Varies: short for emphasis, longer for explanation.",
    signature_moves=[
        "Be specific, not general — name the thing, don't describe its category",
        "Have a clear point of view — don't be neutral",
        "One idea per paragraph",
    ],
    avoid=["Clichés", "Passive voice"],
    cta_style="One clear, specific action or question.",
)

# ---------------------------------------------------------------------------
# Registry and lookup
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, StyleContext] = {
    s.id: s for s in [
        TechnicalEducatorStyle, ContraryExpertStyle, FounderStorytellerStyle,
        MinimalistOperatorStyle, StrategicAdvisorStyle, StorytellerStyle, AnalystStyle,
    ]
}

_ALIASES: dict[str, str] = {
    "technical educator":    "technical_educator",
    "educator":              "technical_educator",
    "explainer":             "technical_educator",
    "contrarian expert":     "contrarian_expert",
    "contrarian":            "contrarian_expert",
    "challenger":            "contrarian_expert",
    "founder storyteller":   "founder_storyteller",
    "founder":               "founder_storyteller",
    "founder voice":         "founder_storyteller",
    "minimalist":            "minimalist_operator",
    "minimalist operator":   "minimalist_operator",
    "operator":              "minimalist_operator",
    "strategic advisor":     "strategic_advisor",
    "advisor":               "strategic_advisor",
    "strategic":             "strategic_advisor",
    "storyteller":           "storyteller",
    "narrative":             "storyteller",
    "analyst":               "analyst",
    "analytical":            "analyst",
}


def get_style_context(style: str) -> Optional[StyleContext]:
    """Match a style string to a StyleContext. Returns None if not matched."""
    if not style:
        return None
    key = style.lower().strip()
    if key in _REGISTRY:
        return _REGISTRY[key]
    if key in _ALIASES:
        return _REGISTRY.get(_ALIASES[key])
    for alias, sid in _ALIASES.items():
        if alias in key or key in alias:
            return _REGISTRY.get(sid)
    return None


def list_styles() -> list[str]:
    return [s.label for s in _REGISTRY.values()]
