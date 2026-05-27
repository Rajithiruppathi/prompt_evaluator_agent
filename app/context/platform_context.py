"""
Platform Context — typed, composable, self-validating platform rules.

Each PlatformContext instance is a reusable object that:
  - Describes its structural rules (hook, flow, CTA)
  - Knows its hard constraints (word count, hashtags, title, CTA)
  - Serializes itself compactly for prompt injection (to_context_block)
  - Validates output against its constraints (validate_output)

Pre-built instances (importable directly):
  LinkedInContext, BlogContext, ColdEmailContext, AdCopyContext,
  TwitterThreadContext, SEOArticleContext, TechnicalPostContext, EducationalContext

This replaces the platform dict lookups from app/knowledge/platforms/profiles.py
with typed, testable objects while the knowledge base remains the raw data source
for backward-compatible code paths.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlatformContext:
    id: str
    label: str
    # Hook rules
    hook_rules: list[str]
    hook_fails: list[str]
    # Content flow
    structure: list[str]
    structural_notes: list[str] = field(default_factory=list)
    # CTA
    cta_rules: list[str] = field(default_factory=list)
    cta_fails: list[str] = field(default_factory=list)
    # Hard constraints
    max_words: Optional[int] = None
    hashtag_min: int = 0
    hashtag_max: int = 0
    requires_title: bool = False
    requires_cta: bool = False
    max_para_words: Optional[int] = None
    # Platform signals
    native_behaviors: list[str] = field(default_factory=list)
    failure_conditions: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------

    def to_context_block(self) -> str:
        """
        Compact prompt representation.
        Replaces the verbose _platform() section from prompt_optimizer.py.
        Designed to be ~55% shorter with equivalent information density.
        """
        lines = [f"PLATFORM: {self.label}"]
        lines.append(f"Flow: {' → '.join(self.structure)}")

        constraints: list[str] = []
        if self.max_words:
            constraints.append(f"max {self.max_words} words")
        if self.hashtag_min > 0:
            constraints.append(f"hashtags {self.hashtag_min}-{self.hashtag_max} at END only")
        elif self.hashtag_max == 0:
            constraints.append("no hashtags")
        if self.requires_title:
            constraints.append("title/H1 as first line")
        if self.requires_cta:
            constraints.append("explicit CTA in closing")
        if self.max_para_words:
            constraints.append(f"max {self.max_para_words} words/paragraph")
        if constraints:
            lines.append("Constraints: " + " | ".join(constraints))

        if self.hook_rules:
            lines.append("Hook works: " + " | ".join(self.hook_rules[:3]))
        if self.hook_fails:
            lines.append("Hook fails: " + " | ".join(self.hook_fails[:2]))
        if self.cta_rules:
            lines.append("CTA strong: " + " | ".join(self.cta_rules[:2]))
        if self.cta_fails:
            lines.append("CTA weak: " + " | ".join(self.cta_fails[:2]))
        if self.failure_conditions:
            lines.append("Fails when: " + " | ".join(self.failure_conditions[:3]))
        if self.structural_notes:
            lines.append("Structure notes: " + " | ".join(self.structural_notes[:2]))

        return "\n".join(lines)

    def validate_output(self, content: str) -> list[str]:
        """
        Deterministic pre-publish check against platform constraints.
        Returns list of issues. Empty list = clean.

        This is the pre-generation validation the architecture supports —
        runs before the LLM call to verify context integrity, and can run
        post-generation for a fast structural check before expensive repair.
        """
        issues: list[str] = []
        words = content.split()
        word_count = len(words)

        if self.max_words and word_count > self.max_words:
            issues.append(
                f"Length: {word_count} words (max {self.max_words})"
            )

        hashtags = re.findall(r"#\w+", content)
        count = len(hashtags)
        if self.hashtag_max == 0 and self.hashtag_min == 0 and count > 0:
            issues.append(f"Hashtags: {count} found, none allowed for this platform")
        elif self.hashtag_min > 0 and not (self.hashtag_min <= count <= self.hashtag_max):
            issues.append(
                f"Hashtag count: {count} found, expected {self.hashtag_min}-{self.hashtag_max}"
            )

        if self.requires_title:
            first_line = content.strip().split("\n")[0].strip()
            has_title = first_line.startswith("#") or (
                len(first_line) < 80 and not first_line.endswith(".")
            )
            if not has_title:
                issues.append("Missing title or heading as first line")

        if self.requires_cta:
            last_section = content[-max(len(content) // 4, 200):]
            has_cta = "?" in last_section or any(
                w in last_section.lower()
                for w in ["share", "comment", "reply", "try", "book", "follow", "dm", "tell me", "reach out"]
            )
            if not has_cta:
                issues.append("Missing CTA in closing section")

        if self.max_para_words:
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            long_paras = [
                i + 1 for i, p in enumerate(paragraphs)
                if len(p.split()) > self.max_para_words
            ]
            if long_paras:
                issues.append(
                    f"Paragraphs {long_paras} exceed {self.max_para_words} words/paragraph"
                )

        return issues


# ---------------------------------------------------------------------------
# Pre-built platform instances
# ---------------------------------------------------------------------------

LinkedInContext = PlatformContext(
    id="linkedin_post",
    label="LinkedIn Post",
    hook_rules=[
        "Specific number, metric, or production incident",
        "Named tool, constraint, or decision with stakes",
        "Counterintuitive claim a practitioner would recognize as true",
    ],
    hook_fails=[
        "Educational scene-setting or background context",
        "Starting with 'In today's world' or any generic opener",
        "Opening with 'I' followed by something self-congratulatory",
    ],
    structure=["Hook (1-2 sentences)", "Tension / Context", "Insight", "Implication", "CTA"],
    structural_notes=[
        "Max 2 sentences per paragraph — white space is structural",
        "Hashtags on the final line, grouped",
    ],
    cta_rules=[
        "Specific technical question practitioners have a real answer to",
        "Challenge your own stated position — invite pushback",
    ],
    cta_fails=["Let me know your thoughts", "Like and share", "Follow for more"],
    max_words=300,
    hashtag_min=3,
    hashtag_max=5,
    requires_cta=True,
    max_para_words=40,
    native_behaviors=[
        "Reads like one practitioner talking to another",
        "Personal observation, not a policy statement",
        "No educational-article tone",
    ],
    failure_conditions=[
        "Three consecutive paragraphs of similar length",
        "Reads like a blog post introduction",
        "Ends with a question nobody has a strong opinion on",
    ],
)

BlogContext = PlatformContext(
    id="blog",
    label="Blog Post",
    hook_rules=[
        "State the core tension or knowledge gap in the opening paragraph",
        "Surprising data point or counterintuitive framing",
        "Specific scenario the target reader has already faced",
    ],
    hook_fails=[
        "Generic background ('AI is transforming everything')",
        "Defining terms the reader already knows",
        "Burying the thesis under setup",
    ],
    structure=["Title (H1)", "Hook paragraph", "Problem context", "Analysis", "Practical insight", "Conclusion"],
    requires_title=True,
    cta_rules=["Point to the next logical thing to read or do", "Specific question readers can immediately apply"],
    cta_fails=["Vague 'hope this helped'", "Generic newsletter subscribe pitch"],
    native_behaviors=[
        "Subheadings (##) for scannable structure",
        "Paragraphs up to 80 words acceptable",
        "Examples and code samples where relevant",
    ],
    failure_conditions=[
        "Wall of text with no visual breaks",
        "Conclusion that just restates the intro",
        "No concrete takeaway for the reader",
    ],
)

ColdEmailContext = PlatformContext(
    id="cold_email",
    label="Cold Email",
    hook_rules=[
        "Specific observation about the recipient's company, role, or recent work",
        "Problem statement they recognize in the first sentence",
        "One-line hook — no setup, no warm-up",
    ],
    hook_fails=[
        "'Hope this email finds you well'",
        "Long intro about who you are",
        "Vague 'I came across your work'",
    ],
    structure=["Hook (1 sentence)", "Problem they recognize", "What you do about it", "Social proof (1 line)", "Single CTA"],
    max_words=200,
    requires_cta=True,
    cta_rules=["Single low-friction ask: 15-minute call, one question, one link"],
    cta_fails=["Multiple asks in one email", "Vague 'let me know if interested'"],
    native_behaviors=["Under 200 words always", "One CTA, one ask, no exceptions"],
    failure_conditions=[
        "Over 200 words",
        "More than one ask",
        "Opens with 'My name is' or 'I'm reaching out because'",
    ],
)

AdCopyContext = PlatformContext(
    id="ad_copy",
    label="Ad Copy",
    hook_rules=[
        "Lead with the outcome — not the feature",
        "Problem statement in the first 5 words",
        "Specific number or verifiable claim",
    ],
    hook_fails=["Starting with the product name", "Feature-first framing", "Vague benefit claims"],
    structure=["Hook (problem or outcome)", "Proof or mechanism", "CTA"],
    max_words=100,
    requires_cta=True,
    cta_rules=["One specific action verb: Try, Get, Book, Start"],
    cta_fails=["'Learn More'", "'Click Here'", "'Find Out More'"],
    native_behaviors=["Ultra-concise", "Active voice only", "No hedging, no passive"],
    failure_conditions=["Over 100 words", "Multiple CTAs", "No specific claim or number"],
)

TwitterThreadContext = PlatformContext(
    id="twitter_thread",
    label="Twitter Thread",
    hook_rules=[
        "Tweet 1 must work standalone — it's the only tweet most people see",
        "Start with the conclusion or the most counterintuitive claim",
        "Make Tweet 1 so specific and true that practitioners share it without reading Thread",
    ],
    hook_fails=[
        "Long setup before the point",
        "Starting with 'A thread on...'",
        "Tweet 1 requires Tweet 2 to make sense",
    ],
    structure=["Hook tweet", "Supporting tweets (2-3)", "Evidence/example tweet", "Implication", "CTA tweet"],
    native_behaviors=[
        "Each tweet is independently shareable",
        "Use / separator between tweets",
        "Tweet 1 is the only one that matters for reach — optimize it",
    ],
    failure_conditions=[
        "Tweet 1 doesn't stand alone",
        "No clear thread signal in Tweet 1",
        "Ends without a concrete takeaway",
    ],
)

SEOArticleContext = PlatformContext(
    id="seo_article",
    label="SEO Article",
    hook_rules=[
        "Answer the search intent directly in the first paragraph",
        "Include the primary keyword naturally in the H1",
        "State clearly who this is for and what they gain",
    ],
    hook_fails=[
        "Burying the answer under SEO boilerplate",
        "Keyword stuffing in the opening",
        "Generic intro that matches every competing article",
    ],
    structure=["H1 (with keyword)", "Direct answer paragraph", "Deep sections (H2)", "FAQ section", "Conclusion"],
    requires_title=True,
    native_behaviors=[
        "H2/H3 subheadings for scannable structure",
        "FAQ section targets featured snippets",
        "First paragraph directly answers the query",
    ],
    failure_conditions=[
        "No H1 or structured headings",
        "Search intent not addressed until paragraph 3+",
        "No FAQ or featured snippet targeting",
    ],
)

TechnicalPostContext = PlatformContext(
    id="technical_post",
    label="Technical Post",
    hook_rules=[
        "State the specific problem and what you built to solve it",
        "Lead with the constraint that made this non-trivial",
        "Include the specific stack/tools in the opening paragraph",
    ],
    hook_fails=[
        "Starting with 'In this post we will explore'",
        "Background before the actual technical content",
        "Generic description of the technology category",
    ],
    structure=["Problem statement", "Approach", "Implementation", "Key decisions", "Results", "Lessons"],
    requires_title=True,
    native_behaviors=[
        "Code samples where relevant",
        "Numbered steps for processes",
        "Decision tables or tradeoff analysis",
    ],
    failure_conditions=[
        "All theory, no implementation details",
        "Decisions not explained",
        "No concrete outcome, benchmark, or measured result",
    ],
)

EducationalContext = PlatformContext(
    id="educational_content",
    label="Educational Content",
    hook_rules=[
        "Open with the misconception most readers currently hold",
        "State what they'll be able to do after reading",
        "Give the real explanation before the oversimplification",
    ],
    hook_fails=[
        "Starting with a dictionary definition",
        "Bottom-up when top-down is clearer",
        "Academic-paper tone that increases distance",
    ],
    structure=["Misconception or problem", "Correct mental model", "Explanation with example", "Application", "Summary"],
    requires_title=True,
    native_behaviors=[
        "Concrete examples before abstract principles",
        "One concept per section",
        "Analogies grounded in what the reader already understands",
    ],
    failure_conditions=[
        "Jargon without definition",
        "No concrete example anywhere",
        "Ending without telling the reader what to do with the knowledge",
    ],
)

# ---------------------------------------------------------------------------
# Registry and lookup
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, PlatformContext] = {
    p.id: p for p in [
        LinkedInContext, BlogContext, ColdEmailContext, AdCopyContext,
        TwitterThreadContext, SEOArticleContext, TechnicalPostContext, EducationalContext,
    ]
}

_ALIASES: dict[str, str] = {
    "linkedin":             "linkedin_post",
    "linkedin post":        "linkedin_post",
    "blog":                 "blog",
    "blog post":            "blog",
    "cold email":           "cold_email",
    "email":                "cold_email",
    "cold_email":           "cold_email",
    "ad copy":              "ad_copy",
    "ad":                   "ad_copy",
    "twitter":              "twitter_thread",
    "twitter thread":       "twitter_thread",
    "x thread":             "twitter_thread",
    "seo":                  "seo_article",
    "seo article":          "seo_article",
    "technical":            "technical_post",
    "technical post":       "technical_post",
    "educational":          "educational_content",
    "educational content":  "educational_content",
}

_DEFAULT = PlatformContext(
    id="general",
    label="General Content",
    hook_rules=["Lead with the core value", "Specific over generic"],
    hook_fails=["Generic scene-setting", "Buried thesis"],
    structure=["Hook", "Content", "Conclusion"],
)


def get_platform_context(use_case: str) -> PlatformContext:
    """Match a use-case string to a PlatformContext. Returns general default if not matched."""
    key = use_case.lower().strip()
    if key in _REGISTRY:
        return _REGISTRY[key]
    if key in _ALIASES:
        return _REGISTRY.get(_ALIASES[key], _DEFAULT)
    for alias, pid in _ALIASES.items():
        if alias in key or key in alias:
            return _REGISTRY.get(pid, _DEFAULT)
    return _DEFAULT


def list_platforms() -> list[str]:
    return [p.label for p in _REGISTRY.values()]
