"""
Examples Context — curated few-shot examples for prompt injection.

ContentExample objects carry quality annotations and platform/audience tags.
Random sampling ensures variation across requests (different examples each time).

Format produced for prompt injection:
  GOOD EXAMPLE (score ~88/100):
  ---
  [content]
  ---
  Why it works: ...

  BAD EXAMPLE (score ~32/100):
  ---
  [content]
  ---
  Why it fails: ...
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class ContentExample:
    content: str
    quality: Literal["good", "bad"]
    why: str                          # Why it works / why it fails
    platform_ids: list[str]           # Which platforms this example applies to
    audience_ids: list[str]           # Which audiences this example applies to
    score: int = 0                    # Approximate humanization score
    style_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# LinkedIn × AI Engineer / Developer
# ---------------------------------------------------------------------------

_LINKEDIN_ENGINEER_GOOD_1 = ContentExample(
    content=(
        "We deployed a RAG pipeline to production on a Tuesday.\n\n"
        "By Thursday, it was silently returning stale answers because "
        "the embedding model got updated and nobody noticed the vector "
        "space had shifted.\n\n"
        "No alerts. No errors. Just confident-sounding wrong answers.\n\n"
        "The fix wasn't technical. It was operational: we added a nightly "
        "drift check that compares a fixed test query against a known-good "
        "embedding. If cosine similarity drops below 0.92, it pages.\n\n"
        "Embeddings are infrastructure now. Treat them like it.\n\n"
        "What's your embedding drift detection look like?"
    ),
    quality="good",
    why=(
        "Opens mid-incident, not with background. Specific detail (Tuesday, "
        "0.92 threshold) builds credibility. The failure is concrete. "
        "The fix is operational, not theoretical. CTA invites real answers."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["ai_engineer", "developer"],
    score=87,
    style_ids=["technical_educator", "founder_storyteller"],
)

_LINKEDIN_ENGINEER_GOOD_2 = ContentExample(
    content=(
        "Most teams are measuring the wrong thing in their LLM pipelines.\n\n"
        "They track latency and cost. Fair. But they miss the metric that "
        "actually predicts user trust: answer consistency.\n\n"
        "Ask the same question twice, slightly rephrased. If you get "
        "different answers, your users are getting different answers too — "
        "and they're losing confidence in your product without telling you.\n\n"
        "We built a consistency harness that runs 200 query variants "
        "nightly and flags responses where variance exceeds 15%. "
        "It caught a prompt regression three days before a customer "
        "escalation would have.\n\n"
        "Latency is visible. Inconsistency is quiet until it isn't.\n\n"
        "What metrics are you tracking that most teams skip?"
    ),
    quality="good",
    why=(
        "Leads with a counterintuitive claim practitioners recognize. "
        "Specific numbers (200 variants, 15%) signal real implementation. "
        "The consequence (customer escalation) is concrete. "
        "CTA asks a real practitioner question."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["ai_engineer", "developer"],
    score=84,
    style_ids=["contrarian_expert", "analyst"],
)

_LINKEDIN_ENGINEER_BAD_1 = ContentExample(
    content=(
        "In today's fast-paced world of AI, it's important to leverage "
        "the power of RAG to empower your teams and unlock new possibilities.\n\n"
        "RAG (Retrieval Augmented Generation) is a groundbreaking approach "
        "that combines the best of both worlds: retrieval and generation.\n\n"
        "Here are 5 ways RAG can transform your business:\n"
        "1. Better answers\n"
        "2. More relevant results\n"
        "3. Reduced hallucinations\n"
        "4. Improved user experience\n"
        "5. Scalable solutions\n\n"
        "If you found this valuable, like and share with your network!\n\n"
        "#AI #RAG #MachineLearning #Innovation #Technology"
    ),
    quality="bad",
    why=(
        "Opens with a banned robotic phrase ('In today's fast-paced world'). "
        "Defines RAG for an audience that built RAG systems. "
        "Generic numbered list with no implementation detail. "
        "Weak CTA ('like and share'). AI-vocabulary overload (leverage, "
        "empower, unlock, groundbreaking, transform, scalable)."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["ai_engineer", "developer"],
    score=18,
    style_ids=[],
)

# ---------------------------------------------------------------------------
# LinkedIn × Founder / Startup
# ---------------------------------------------------------------------------

_LINKEDIN_FOUNDER_GOOD_1 = ContentExample(
    content=(
        "We almost killed the company by hiring too fast.\n\n"
        "Month 8. $1.2M ARR. Two enterprise deals pending. "
        "We hired 4 engineers and a head of sales in 6 weeks.\n\n"
        "The sales hire closed nothing for 90 days. "
        "Two of the engineers built features nobody asked for. "
        "The team that had shipped weekly started missing sprints.\n\n"
        "I'd confused revenue momentum with organizational readiness. "
        "They're not the same thing.\n\n"
        "What we should have done: close the enterprise deals first, "
        "then hire the people to support what we'd proven — not what we expected.\n\n"
        "What was the hiring mistake that almost broke your momentum?"
    ),
    quality="good",
    why=(
        "Drops directly into a specific situation (month 8, $1.2M ARR). "
        "Numbers are concrete, not rounded. The failure is real and "
        "specific — not generic 'fail fast' wisdom. The lesson emerges "
        "from the story rather than being stated first. CTA asks for "
        "their version."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["startup_founder"],
    score=91,
    style_ids=["founder_storyteller"],
)

_LINKEDIN_FOUNDER_BAD_1 = ContentExample(
    content=(
        "As entrepreneurs, we all know the importance of resilience and "
        "having a growth mindset. In today's competitive landscape, it's "
        "essential to leverage every opportunity to create value.\n\n"
        "Here's what separates successful founders from the rest:\n"
        "✅ They fail fast and learn faster\n"
        "✅ They build systems, not just products\n"
        "✅ They focus on the long game\n"
        "✅ They surround themselves with the right people\n\n"
        "Remember: your journey is unique. Trust the process!\n\n"
        "What's your biggest lesson as a founder? Share below! 👇\n\n"
        "#Entrepreneurship #Founder #StartupLife #GrowthMindset #Leadership"
    ),
    quality="bad",
    why=(
        "Generic lessons that apply to nothing ('fail fast', 'trust the process'). "
        "Checkmark list removes any specificity. No real incident, no real stakes. "
        "Uses banned phrases: 'leverage', 'in today's competitive landscape', "
        "'create value'. Emoji-heavy CTA feels performative. "
        "Anyone could have written this without having built anything."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["startup_founder"],
    score=12,
    style_ids=[],
)

# ---------------------------------------------------------------------------
# Cold Email
# ---------------------------------------------------------------------------

_COLD_EMAIL_GOOD_1 = ContentExample(
    content=(
        "Your engineering blog post on the Postgres connection pooling fix "
        "saved us 3 days of debugging last month.\n\n"
        "We're building a similar observability layer for LLM pipelines — "
        "specifically tracking token drift and embedding consistency across "
        "model versions.\n\n"
        "We've reduced silent failure rate by 40% in our first 6 customers. "
        "Would a 20-minute call make sense to see if it fits your stack?"
    ),
    quality="good",
    why=(
        "Specific observation about recipient's actual work (blog post). "
        "Immediate problem statement they recognize. "
        "Social proof is concrete (40%, 6 customers). "
        "Single low-friction ask (20-minute call). Under 100 words."
    ),
    platform_ids=["cold_email"],
    audience_ids=["ai_engineer", "developer"],
    score=88,
    style_ids=["minimalist_operator"],
)

_COLD_EMAIL_BAD_1 = ContentExample(
    content=(
        "Hi [Name],\n\n"
        "I hope this email finds you well! My name is Alex and I'm "
        "reaching out because I came across your profile and thought "
        "there might be a great opportunity for mutual benefit.\n\n"
        "I wanted to touch base about our revolutionary AI-powered platform "
        "that leverages cutting-edge technology to empower your team and "
        "drive results.\n\n"
        "Our solution is a game-changer for companies like yours. "
        "We'd love to schedule a call to discuss how we can create "
        "synergies between our organizations.\n\n"
        "Looking forward to hearing from you!\n\n"
        "Best regards,\nAlex"
    ),
    quality="bad",
    why=(
        "Opens with banned phrase ('hope this email finds you well'). "
        "'I'm reaching out because' is one of the most filtered-on phrases. "
        "No specific observation about the recipient. "
        "AI-vocabulary overload: revolutionary, leverage, cutting-edge, "
        "empower, game-changer, synergies. "
        "Two vague asks instead of one. Over 100 words."
    ),
    platform_ids=["cold_email"],
    audience_ids=["ai_engineer", "developer", "startup_founder", "enterprise_buyer"],
    score=8,
    style_ids=[],
)

# ---------------------------------------------------------------------------
# Blog × Technical
# ---------------------------------------------------------------------------

_BLOG_TECHNICAL_GOOD_1 = ContentExample(
    content=(
        "# Why Your LLM Eval Framework Fails Under Real Load\n\n"
        "Most eval frameworks break the same way: they test what you expect, "
        "not what users actually do.\n\n"
        "We ran 50,000 real user queries through our eval pipeline. "
        "62% of failures came from query patterns that weren't in our "
        "test set at all — edge cases, typos, domain-specific abbreviations, "
        "and questions phrased as complaints rather than queries.\n\n"
        "The problem isn't the LLM. It's the eval distribution."
    ),
    quality="good",
    why=(
        "H1 states the specific problem with the audience in mind. "
        "First paragraph frames the core flaw without background setup. "
        "Specific numbers (50,000 queries, 62%) give immediate credibility. "
        "Ends with a sharp, quotable insight — not a summary."
    ),
    platform_ids=["blog", "technical_post"],
    audience_ids=["ai_engineer", "developer"],
    score=85,
    style_ids=["technical_educator", "analyst"],
)

_BLOG_TECHNICAL_BAD_1 = ContentExample(
    content=(
        "# The Ultimate Guide to LLM Evaluation\n\n"
        "In this comprehensive guide, we will explore everything you need "
        "to know about evaluating large language models. "
        "LLMs are a type of AI that can generate text, and evaluating them "
        "is important for ensuring quality.\n\n"
        "In this article we will cover:\n"
        "- What is an LLM?\n"
        "- Why evaluation matters\n"
        "- Types of evaluation\n"
        "- Best practices\n"
        "- Conclusion\n\n"
        "Stay tuned for more great content on AI!"
    ),
    quality="bad",
    why=(
        "Title uses banned SEO cliché ('The Ultimate Guide', 'everything you need'). "
        "Defines LLMs for an audience that builds them. "
        "Table of contents as opening content delays the actual insight. "
        "Uses banned blog phrases: 'in this comprehensive guide', "
        "'in this article we will cover', 'stay tuned'. "
        "No specific claim, no data, nothing a reader couldn't have predicted."
    ),
    platform_ids=["blog", "seo_article"],
    audience_ids=["ai_engineer", "developer"],
    score=11,
    style_ids=[],
)

# ---------------------------------------------------------------------------
# Ad Copy
# ---------------------------------------------------------------------------

_AD_COPY_GOOD_1 = ContentExample(
    content=(
        "Your LLM is hallucinating in production right now.\n\n"
        "Most teams don't know until a customer screenshot goes viral.\n\n"
        "Guardrail catches it before they do.\n\n"
        "Try free for 14 days."
    ),
    quality="good",
    why=(
        "Leads with the problem the audience already has. "
        "'Right now' creates immediate relevance. "
        "The consequence is specific and painful (screenshot going viral). "
        "Brand name appears only after the problem is established. "
        "CTA is a single verb with a specific offer. Under 40 words."
    ),
    platform_ids=["ad_copy"],
    audience_ids=["ai_engineer", "developer", "startup_founder"],
    score=90,
    style_ids=["minimalist_operator"],
)

_AD_COPY_BAD_1 = ContentExample(
    content=(
        "Introducing GuardRail AI — the revolutionary, game-changing platform "
        "that leverages cutting-edge artificial intelligence to empower your "
        "team with world-class LLM monitoring solutions!\n\n"
        "Our holistic approach drives results and moves the needle on "
        "quality. Best-in-class technology for forward-thinking teams.\n\n"
        "Learn More | Find Out More | Click Here"
    ),
    quality="bad",
    why=(
        "Leads with product name instead of problem. "
        "Banned vocabulary density: revolutionary, game-changing, leverages, "
        "cutting-edge, empower, world-class, holistic approach, "
        "drives results, moves the needle, best-in-class. "
        "Three weak CTAs instead of one strong one ('Learn More', "
        "'Find Out More', 'Click Here' are all banned). "
        "Zero specificity — no number, no concrete claim."
    ),
    platform_ids=["ad_copy"],
    audience_ids=["ai_engineer", "developer", "startup_founder", "enterprise_buyer"],
    score=5,
    style_ids=[],
)

# ---------------------------------------------------------------------------
# Twitter Thread
# ---------------------------------------------------------------------------

_TWITTER_GOOD_1 = ContentExample(
    content=(
        "Your LLM's confidence score is lying to you.\n\n"
        "High logprob ≠ correct answer. It means the model is certain about "
        "its wrong answer. That's worse.\n\n"
        "/\n\n"
        "We tested this with medical triage queries. Model returned "
        "0.97 confidence on an answer that 3 out of 5 clinicians flagged wrong.\n\n"
        "High confidence, high stakes, high risk.\n\n"
        "/\n\n"
        "The fix: calibration, not confidence. "
        "Train humans to treat model confidence as a prior, not a verdict.\n\n"
        "/\n\n"
        "What's the highest-confidence wrong answer you've seen from an LLM?"
    ),
    quality="good",
    why=(
        "Tweet 1 works completely standalone — makes a counterintuitive claim "
        "practitioners will immediately react to. "
        "Each section adds a new layer, not just repetition. "
        "Specific domain (medical triage) and data point (3/5 clinicians). "
        "CTA invites real examples from practitioners."
    ),
    platform_ids=["twitter_thread"],
    audience_ids=["ai_engineer", "developer"],
    score=86,
    style_ids=["contrarian_expert", "analyst"],
)

_TWITTER_BAD_1 = ContentExample(
    content=(
        "A thread on why AI is important in 2024 🧵\n\n"
        "/\n\n"
        "First, let me explain what AI is...\n\n"
        "/\n\n"
        "There are many types of AI including machine learning, "
        "deep learning, and neural networks.\n\n"
        "/\n\n"
        "AI can help businesses in many ways:\n"
        "- Better efficiency\n"
        "- Cost savings\n"
        "- Improved outcomes\n\n"
        "/\n\n"
        "Thanks for reading! Like and retweet if you found this valuable!"
    ),
    quality="bad",
    why=(
        "Opens with 'A thread on...' — banned pattern that kills reach. "
        "Tweet 1 announces the topic instead of making a claim. "
        "Defines AI for an audience that builds AI. "
        "Generic benefits list with no specificity. "
        "Ends with a weak engagement beg instead of a real question. "
        "Tweet 1 gives no reason to read Tweet 2."
    ),
    platform_ids=["twitter_thread"],
    audience_ids=["ai_engineer", "developer", "startup_founder"],
    score=9,
    style_ids=[],
)

# ---------------------------------------------------------------------------
# Marketer / SEO audience
# ---------------------------------------------------------------------------

_LINKEDIN_MARKETER_GOOD_1 = ContentExample(
    content=(
        "We cut our content production time by 60% and engagement dropped.\n\n"
        "That was the signal we needed.\n\n"
        "The bottleneck wasn't production speed — it was strategic "
        "thinking about what to produce. When we moved faster, we just "
        "made more of the wrong things faster.\n\n"
        "The fix: one positioning session per quarter where we decide "
        "what NOT to write. Everything else follows from that.\n\n"
        "Content strategy is a subtraction problem, not an addition one.\n\n"
        "What's on your 'don't produce' list?"
    ),
    quality="good",
    why=(
        "Counterintuitive opening (faster production = worse results). "
        "The twist is specific and credible. "
        "The insight is a reframe, not a tip. "
        "CTA is unusual — asks about what they remove, not what they add."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["marketer", "seo_expert"],
    score=83,
    style_ids=["contrarian_expert", "strategic_advisor"],
)

# ---------------------------------------------------------------------------
# Enterprise Buyer audience
# ---------------------------------------------------------------------------

_LINKEDIN_ENTERPRISE_GOOD_1 = ContentExample(
    content=(
        "The vendor said implementation would take 6 weeks.\n\n"
        "We planned for 12. It took 19.\n\n"
        "Not because the technology failed — because nobody mapped "
        "the 14 internal approvals the data governance policy required "
        "before we could connect a single data source.\n\n"
        "Enterprise AI projects fail at procurement and compliance, "
        "not at the model level. The technical evaluation is the easy part.\n\n"
        "Before the next pilot: ask your vendor for their data governance "
        "checklist. If they don't have one, that's your answer.\n\n"
        "What's the approval bottleneck that surprised you most?"
    ),
    quality="good",
    why=(
        "Specific timeline numbers build immediate credibility. "
        "The failure mode is operational, not technical — resonates "
        "with enterprise buyers who live in procurement reality. "
        "The advice is concrete and actionable (ask for the checklist). "
        "CTA invites shared frustration."
    ),
    platform_ids=["linkedin_post"],
    audience_ids=["enterprise_buyer"],
    score=89,
    style_ids=["strategic_advisor", "founder_storyteller"],
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_ALL_EXAMPLES: list[ContentExample] = [
    _LINKEDIN_ENGINEER_GOOD_1,
    _LINKEDIN_ENGINEER_GOOD_2,
    _LINKEDIN_ENGINEER_BAD_1,
    _LINKEDIN_FOUNDER_GOOD_1,
    _LINKEDIN_FOUNDER_BAD_1,
    _COLD_EMAIL_GOOD_1,
    _COLD_EMAIL_BAD_1,
    _BLOG_TECHNICAL_GOOD_1,
    _BLOG_TECHNICAL_BAD_1,
    _AD_COPY_GOOD_1,
    _AD_COPY_BAD_1,
    _TWITTER_GOOD_1,
    _TWITTER_BAD_1,
    _LINKEDIN_MARKETER_GOOD_1,
    _LINKEDIN_ENTERPRISE_GOOD_1,
]


def get_examples(
    platform_id: str = "",
    audience_id: str = "",
    n_good: int = 1,
    n_bad: int = 1,
    style_id: str = "",
) -> tuple[list[ContentExample], list[ContentExample]]:
    """
    Return (good_examples, bad_examples) for the given context.

    Scoring: exact match on platform+audience > platform only > audience only > all.
    Random sampling within the matched set ensures variation across requests.
    """
    def _score(ex: ContentExample) -> int:
        s = 0
        if platform_id and platform_id in ex.platform_ids:
            s += 2
        if audience_id and audience_id in ex.audience_ids:
            s += 2
        if style_id and style_id in ex.style_ids:
            s += 1
        return s

    good = [e for e in _ALL_EXAMPLES if e.quality == "good"]
    bad = [e for e in _ALL_EXAMPLES if e.quality == "bad"]

    good_scored = sorted(good, key=_score, reverse=True)
    bad_scored = sorted(bad, key=_score, reverse=True)

    # Take top candidates, then randomly sample for variation
    top_good = good_scored[:max(n_good * 3, 3)]
    top_bad = bad_scored[:max(n_bad * 3, 3)]

    selected_good = random.sample(top_good, min(n_good, len(top_good)))
    selected_bad = random.sample(top_bad, min(n_bad, len(top_bad)))

    return selected_good, selected_bad


def format_for_prompt(
    good: list[ContentExample],
    bad: list[ContentExample],
) -> str:
    """
    Format examples for prompt injection.
    Shows what 'good' looks like and what 'bad' looks like — with explanations.
    """
    lines: list[str] = []

    for ex in good:
        lines.append(f"GOOD EXAMPLE (score ~{ex.score}/100):")
        lines.append("---")
        lines.append(ex.content.strip())
        lines.append("---")
        lines.append(f"Why it works: {ex.why}")
        lines.append("")

    for ex in bad:
        lines.append(f"BAD EXAMPLE (score ~{ex.score}/100):")
        lines.append("---")
        lines.append(ex.content.strip())
        lines.append("---")
        lines.append(f"Why it fails: {ex.why}")
        lines.append("")

    return "\n".join(lines).strip()
