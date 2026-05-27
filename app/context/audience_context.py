"""
Audience Context — typed, self-describing audience profiles.

Each AudienceContext instance is a reusable object that:
  - Describes who the audience is (background, knowledge level)
  - Defines what earns and breaks their trust
  - Specifies vocabulary to use and avoid
  - Serializes itself compactly for prompt injection (to_context_block)

Pre-built instances (importable directly):
  EngineerAudienceContext, FounderAudienceContext, MarketerAudienceContext,
  DeveloperAudienceContext, StudentAudienceContext, EnterpriseBuyerContext,
  SEOExpertContext, GeneralProfessionalContext
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AudienceContext:
    id: str
    label: str
    knowledge_level: str  # "beginner" | "intermediate" | "expert"
    background: str
    scroll_triggers: list[str]
    pain_points: list[str]
    trust_signals: list[str]
    trust_breakers: list[str]
    vocabulary_use: list[str]
    vocabulary_avoid: list[str]
    wants: list[str]
    hates: list[str]
    cta_preferences: list[str]
    preferred_format: str = "flexible"
    depth: str = "intermediate"

    def to_context_block(self) -> str:
        """
        Compact audience context for prompt injection.
        ~60% shorter than the old _audience() section, equivalent signal.
        """
        lines = [f"AUDIENCE: {self.label} ({self.knowledge_level})"]
        lines.append(f"Background: {self.background}")

        if self.scroll_triggers:
            lines.append(f"Scroll-stop trigger: {self.scroll_triggers[0]}")
        if self.pain_points:
            lines.append("Pain points: " + " | ".join(self.pain_points[:3]))
        if self.trust_signals:
            lines.append("Earns trust: " + " | ".join(self.trust_signals[:2]))
        if self.trust_breakers:
            lines.append("Breaks trust: " + " | ".join(self.trust_breakers[:2]))
        if self.vocabulary_use:
            lines.append("Use: " + ", ".join(self.vocabulary_use[:5]))
        if self.vocabulary_avoid:
            lines.append("Avoid: " + ", ".join(self.vocabulary_avoid[:4]))
        if self.cta_preferences:
            lines.append(f"CTA style: {self.cta_preferences[0]}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pre-built audience instances
# ---------------------------------------------------------------------------

EngineerAudienceContext = AudienceContext(
    id="ai_engineer",
    label="AI / ML Engineer",
    knowledge_level="expert",
    background=(
        "Works daily with LLMs, embeddings, and inference infrastructure. "
        "Has strong opinions forged in production experience."
    ),
    scroll_triggers=[
        "A specific production failure or metric they haven't seen before",
        "A claim that contradicts what the documentation says",
        "An implementation detail that saves real engineering hours",
    ],
    pain_points=[
        "Context window limits and chunking coherence tradeoffs",
        "Eval metrics that don't correlate with production quality",
        "Latency and cost at scale",
        "Hallucination in structured-output use cases",
    ],
    trust_signals=[
        "Specific benchmark numbers with methodology disclosed",
        "Named tools and real production configuration",
        "Acknowledging tradeoffs and what the approach doesn't solve",
    ],
    trust_breakers=[
        "Using 'embeddings' as a generic term for anything AI-related",
        "Benchmarks without production context or scale",
        "Overpromised simplicity",
    ],
    vocabulary_use=["inference", "context window", "latency p99", "eval", "finetuning", "RAG", "embedding", "throughput"],
    vocabulary_avoid=["AI-powered", "cutting-edge AI", "next-generation", "smart AI"],
    wants=[
        "Specific implementation decisions, not just concepts",
        "Production numbers and failure modes",
        "Honest tradeoff analysis with named constraints",
    ],
    hates=[
        "Oversimplified analogies that collapse under scrutiny",
        "Advice that only applies to toy demos",
        "Generic AI content not written by a practitioner",
    ],
    cta_preferences=[
        "Ask a specific technical question they'd actually debate among peers",
        "Challenge them to share their production approach",
    ],
    preferred_format="technical, dense, short paragraphs",
    depth="expert",
)

FounderAudienceContext = AudienceContext(
    id="startup_founder",
    label="Startup Founder",
    knowledge_level="intermediate",
    background=(
        "Building a company. Makes decisions under uncertainty with limited data. "
        "Reads to avoid costly mistakes, not to learn concepts."
    ),
    scroll_triggers=[
        "A decision they're currently facing — described more precisely than they could",
        "A mistake they've privately made but haven't seen written about honestly",
        "A take that challenges the standard startup playbook with evidence",
    ],
    pain_points=[
        "Hiring decisions that change company trajectory",
        "Knowing when to pivot vs. persist with a painful honest evaluation",
        "Metrics that look good internally but don't translate to revenue",
        "Scaling infrastructure before product-market fit is confirmed",
    ],
    trust_signals=[
        "Specific company decisions, numbers, and consequences — not just principles",
        "Acknowledging where the advice breaks down or has conditions",
        "Written by someone who has made the actual decision, not advised on it",
    ],
    trust_breakers=[
        "Generic startup advice without context about stage or constraints",
        "Survivorship bias — success stories without the failures that informed them",
        "Advice from people who've only advised founders, not been one",
    ],
    vocabulary_use=["runway", "PMF", "churn", "CAC", "LTV", "conversion", "pipeline", "cohort"],
    vocabulary_avoid=["hustle", "grind", "10x", "crushing it", "fail fast"],
    wants=[
        "Real decision frameworks with conditions, not just principles",
        "Specific: what to do AND what not to do AND when",
        "Honest accounts of failure with the precise cause named",
    ],
    hates=[
        "Survivorship bias dressed as strategy",
        "Series-B advice applied to pre-product companies",
        "Motivational content that erases the real texture of the experience",
    ],
    cta_preferences=[
        "Ask about a specific decision they're currently facing",
        "Invite them to share the version of this story they lived",
    ],
    preferred_format="narrative, first-person, specific decisions with stakes",
    depth="intermediate",
)

MarketerAudienceContext = AudienceContext(
    id="marketer",
    label="Marketer",
    knowledge_level="intermediate",
    background=(
        "Responsible for campaigns, content, and pipeline. "
        "Measured on performance numbers. Skeptical of tactics without data."
    ),
    scroll_triggers=[
        "A specific channel or tactic they're currently running — described more accurately than their reports",
        "A result (a number) they wish they'd hit or a mistake they recognize",
        "A framework that replaces something they're doing manually and poorly",
    ],
    pain_points=[
        "Attribution across long buying cycles with limited signal",
        "Content that ranks but doesn't convert",
        "Proving marketing's impact on revenue to leadership",
        "Budget allocation across channels without clean last-touch data",
    ],
    trust_signals=[
        "Specific campaign metrics with enough context to evaluate them",
        "Methodology disclosed: what was tested against what control",
        "Acknowledging what didn't work alongside what did",
    ],
    trust_breakers=[
        "Anecdotal 'this always works' without data or conditions",
        "Tactics that require enterprise budgets reapplied to scrappy teams",
        "Advice written before iOS 14 that hasn't been revisited",
    ],
    vocabulary_use=["conversion rate", "CAC", "pipeline", "attribution", "intent signal", "content velocity"],
    vocabulary_avoid=["viral", "explosive growth", "guaranteed results", "growth hacking"],
    wants=[
        "Tactics with enough context to judge whether they apply",
        "Specific results from real campaigns — not case study PR",
        "Frameworks that account for actual resource constraints",
    ],
    hates=[
        "Vague 'create great content' advice",
        "Vanity metrics presented as pipeline impact",
        "Advice that only scales with a 10-person content team",
    ],
    cta_preferences=[
        "Ask about their current channel mix or attribution challenge",
        "Challenge them on a tactic they're running",
    ],
    preferred_format="structured, data-supported, scannable",
    depth="intermediate",
)

DeveloperAudienceContext = AudienceContext(
    id="developer",
    label="Developer",
    knowledge_level="intermediate",
    background=(
        "Builds software professionally. Pragmatic. Cares about correctness, "
        "performance, and code that doesn't break in six months."
    ),
    scroll_triggers=[
        "A bug pattern or gotcha they've hit or are about to hit",
        "A specific library or tool they use daily — described with precision",
        "A decision between two approaches they're currently weighing",
    ],
    pain_points=[
        "Technical debt that slows delivery without a clear payoff",
        "Debugging hard-to-reproduce production issues",
        "Dependencies that update and break things silently",
        "Code review bottlenecks in fast-moving teams",
    ],
    trust_signals=[
        "Working code samples — not pseudocode",
        "Specific version numbers and compatibility context",
        "Honest about when the approach breaks or has limits",
    ],
    trust_breakers=[
        "Pseudocode when a real example was possible",
        "Solutions that work in demos but not in production codebases",
        "Missing error handling in examples",
    ],
    vocabulary_use=["dependency", "refactor", "regression", "CI/CD", "test coverage", "API"],
    vocabulary_avoid=["ninja", "rockstar", "10x developer", "magic", "hack"],
    wants=[
        "Concrete, runnable examples",
        "Specific error messages and their fixes",
        "Decision criteria — not just the conclusion",
    ],
    hates=[
        "Tutorial content adapted for clean slates, not real codebases",
        "Solutions that assume no existing dependencies",
        "Advice that doesn't acknowledge breaking changes",
    ],
    cta_preferences=[
        "Point to the exact file or pattern that applies",
        "Ask about their approach to the same problem",
    ],
    preferred_format="code-heavy, structured, scannable headers",
    depth="intermediate",
)

StudentAudienceContext = AudienceContext(
    id="student",
    label="Student",
    knowledge_level="beginner",
    background=(
        "Actively building mental models. Values clarity and patience over efficiency. "
        "Learning for the first time — not re-learning."
    ),
    scroll_triggers=[
        "A concept explained without assuming prior knowledge",
        "A clear 'why this matters' before the how",
        "Honest acknowledgment that something is genuinely hard — and a path through it",
    ],
    pain_points=[
        "Tutorials that skip steps they don't have context for yet",
        "Documentation written for people who already know the answer",
        "Concepts explained using other concepts they don't know yet",
    ],
    trust_signals=[
        "Step-by-step with no gaps",
        "Explicit about prerequisites",
        "Defines every term before using it",
    ],
    trust_breakers=[
        "'Simply' or 'just' before complex steps",
        "No explanation of why — only how",
        "No error handling for common beginner mistakes",
    ],
    vocabulary_use=["for example", "this means", "which is", "in other words", "specifically"],
    vocabulary_avoid=["obviously", "trivially", "of course", "as you know"],
    wants=[
        "Building blocks that compound — not isolated facts",
        "Examples before abstractions",
        "Explicit connections between concepts",
    ],
    hates=[
        "Assumed context",
        "Expert vocabulary without definition",
        "Impatience or condescension in the writing",
    ],
    cta_preferences=[
        "Encourage them to try the example themselves",
        "Point to the next concept in sequence",
    ],
    preferred_format="step-by-step, example-first, patient, visual",
    depth="beginner",
)

EnterpriseBuyerContext = AudienceContext(
    id="enterprise_buyer",
    label="Enterprise Buyer",
    knowledge_level="intermediate",
    background=(
        "Evaluating solutions with stakeholder management and procurement overhead. "
        "Balancing technical, operational, and financial risk. Not the end user."
    ),
    scroll_triggers=[
        "A specific integration or compliance question they're currently blocked on",
        "A risk they hadn't considered that changes the evaluation",
        "Evidence from a company comparable to theirs in industry and size",
    ],
    pain_points=[
        "Hidden integration costs discovered after procurement closes",
        "Vendor lock-in and data portability questions",
        "Internal change management and adoption",
        "Budget justification to non-technical leadership",
    ],
    trust_signals=[
        "Named case studies with comparable companies and specific outcomes",
        "Transparent implementation timeline and resource requirements",
        "Security certifications and data residency documentation",
    ],
    trust_breakers=[
        "Vague pricing ('contact us for pricing')",
        "ROI claims without disclosed methodology",
        "References that don't match their industry",
    ],
    vocabulary_use=["ROI", "TCO", "SLA", "compliance", "integration", "security", "procurement"],
    vocabulary_avoid=["cheap", "quick fix", "hack", "workaround", "startup-friendly"],
    wants=[
        "Proof from comparable organizations with named outcomes",
        "Clear implementation path and realistic timeline",
        "Risk mitigation evidence and exit options",
    ],
    hates=[
        "Marketing claims without verifiable evidence",
        "Demos that don't map to real enterprise workflows",
        "Hidden requirements discovered after contract",
    ],
    cta_preferences=[
        "Offer a structured proof of concept or evaluation framework",
        "Reference a security or compliance document",
    ],
    preferred_format="structured, evidence-based, formal",
    depth="intermediate",
)

SEOExpertContext = AudienceContext(
    id="seo_expert",
    label="SEO Expert",
    knowledge_level="expert",
    background=(
        "Works with search algorithms, content strategy, and technical audits. "
        "Measures everything. Highly skeptical of vanity metrics and agency claims."
    ),
    scroll_triggers=[
        "A ranking factor or algorithm change backed by real data — not speculation",
        "A case study with before/after traffic AND conversion numbers",
        "A workflow or tool that reduces audit time without sacrificing accuracy",
    ],
    pain_points=[
        "Core Web Vitals and technical debt at scale",
        "E-E-A-T signals that are hard to systematize",
        "Content cannibalization across large sites",
        "Proving SEO ROI to leadership without vanity metrics",
    ],
    trust_signals=[
        "Real search volume and ranking data with methodology",
        "Acknowledging when something stopped working and why",
        "Specific tools and configurations, not just categories",
    ],
    trust_breakers=[
        "Traffic numbers without conversion context",
        "Tactics from before major algorithm updates presented as current",
        "Keyword stuffing repackaged as strategy",
    ],
    vocabulary_use=["SERP", "E-E-A-T", "Core Web Vitals", "cannibalization", "featured snippet", "crawl budget"],
    vocabulary_avoid=["gaming Google", "trick", "guaranteed ranking", "hack"],
    wants=[
        "Case studies with reproducible methodology and disclosed constraints",
        "Technical implementation specifics, not category descriptions",
        "Honest account of what stopped working",
    ],
    hates=[
        "Content written for search engines that ignores user intent",
        "Traffic metrics disconnected from business outcomes",
        "Advice that was accurate three algorithm updates ago",
    ],
    cta_preferences=[
        "Ask about their current approach to the specific tactic discussed",
        "Challenge them on a metric they're using as a success signal",
    ],
    preferred_format="data-dense, structured, scannable with clear methodology",
    depth="expert",
)

GeneralProfessionalContext = AudienceContext(
    id="general_professional",
    label="General Professional",
    knowledge_level="intermediate",
    background=(
        "Smart working professional without deep domain specialization. "
        "Values clarity, practicality, and brevity. Time is the real constraint."
    ),
    scroll_triggers=[
        "A specific insight that applies immediately to their situation",
        "Recognition of a problem they have but haven't named precisely",
        "A counterintuitive claim backed by visible reasoning",
    ],
    pain_points=[
        "Too much information, not enough clarity on what to do",
        "Advice that doesn't account for organizational complexity",
        "Principles without practical application or conditions",
    ],
    trust_signals=[
        "Specific examples, not just principles",
        "Acknowledges when advice doesn't apply",
        "Written by someone who has done it",
    ],
    trust_breakers=[
        "Jargon without definition",
        "Advice that only works under ideal conditions",
        "Confident claims without visible evidence",
    ],
    vocabulary_use=["specific", "practical", "clear", "decision", "outcome", "tradeoff"],
    vocabulary_avoid=["synergy", "leverage", "paradigm", "holistic", "robust"],
    wants=["Clear takeaways", "Specific actions with conditions", "Honest about limitations"],
    hates=["Vague platitudes", "Overpromising", "Content that wastes their time"],
    cta_preferences=["One clear, specific question or action — not a menu"],
    preferred_format="clear, direct, short paragraphs",
    depth="intermediate",
)

# ---------------------------------------------------------------------------
# Registry and lookup
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, AudienceContext] = {
    a.id: a for a in [
        EngineerAudienceContext, FounderAudienceContext, MarketerAudienceContext,
        DeveloperAudienceContext, StudentAudienceContext, EnterpriseBuyerContext,
        SEOExpertContext, GeneralProfessionalContext,
    ]
}

_ALIASES: dict[str, str] = {
    "ai engineer":          "ai_engineer",
    "ml engineer":          "ai_engineer",
    "ai/ml engineer":       "ai_engineer",
    "machine learning":     "ai_engineer",
    "startup founder":      "startup_founder",
    "founder":              "startup_founder",
    "entrepreneur":         "startup_founder",
    "marketer":             "marketer",
    "marketing":            "marketer",
    "developer":            "developer",
    "software engineer":    "developer",
    "programmer":           "developer",
    "engineer":             "developer",
    "student":              "student",
    "learner":              "student",
    "enterprise":           "enterprise_buyer",
    "enterprise buyer":     "enterprise_buyer",
    "b2b buyer":            "enterprise_buyer",
    "seo":                  "seo_expert",
    "seo expert":           "seo_expert",
    "general":              "general_professional",
    "professional":         "general_professional",
}


def get_audience_context(audience: str) -> AudienceContext:
    """Match an audience string to an AudienceContext."""
    key = audience.lower().strip()
    if key in _REGISTRY:
        return _REGISTRY[key]
    if key in _ALIASES:
        return _REGISTRY.get(_ALIASES[key], GeneralProfessionalContext)
    for alias, aid in _ALIASES.items():
        if alias in key or key in alias:
            return _REGISTRY.get(aid, GeneralProfessionalContext)
    return GeneralProfessionalContext


def list_audiences() -> list[str]:
    return [a.label for a in _REGISTRY.values()]
