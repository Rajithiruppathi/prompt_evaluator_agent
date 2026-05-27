"""
Audience profiles — the foundation of all audience intelligence.

Each profile captures:
  - Who this person is and what they know
  - What they actually struggle with (not generic pain points)
  - How they consume content (what they skip vs. what they stop for)
  - Vocabulary they trust vs. vocabulary that loses them
  - What earns their trust and what breaks it

Adding a new audience: copy any profile, change the ID and aliases, update all fields.
The system will automatically pick it up — no other code changes needed.
"""

PROFILES: dict[str, dict] = {

    "ai_engineer": {
        "id": "ai_engineer",
        "label": "AI / ML Engineer",
        "aliases": [
            "ai engineer", "ml engineer", "machine learning", "data scientist",
            "nlp", "llm engineer", "ai researcher", "deep learning", "research engineer",
        ],
        "knowledge_level": "expert",
        "background": (
            "Works daily with LLMs, embeddings, RAG pipelines, and inference systems. "
            "Reads papers, ships to production, costs tokens, measures latency."
        ),
        "pain_points": [
            "LLM outputs are non-deterministic — debugging production failures is painful",
            "Evaluation is broken — there's no reliable metric for 'good output'",
            "RAG pipelines hallucinate on edge cases no one thought to test",
            "Context window limits force tradeoffs that change the whole architecture",
            "Prompt fragility: works in dev, breaks in prod with slightly different input",
            "Non-technical stakeholders don't understand why this is hard",
            "Tool churn — a new framework every month claiming to solve everything",
        ],
        "vocabulary": {
            "use": [
                "inference", "fine-tuning", "embedding", "latency", "throughput",
                "RAG", "agent loop", "context window", "hallucination", "evals",
                "token budget", "prompt injection", "chain-of-thought", "grounding",
            ],
            "avoid": [
                "AI magic", "next-gen", "revolutionary", "game-changing",
                "leverage AI", "unlock potential", "powerful algorithms",
            ],
        },
        "content_preferences": {
            "wants": [
                "Specific benchmarks and tradeoff numbers, not vague claims",
                "Honest failure analysis — what breaks, not just what works",
                "Code-backed explanations and real implementation details",
                "Production findings that contradict the documentation",
                "Novel approaches they haven't already seen in obvious papers",
            ],
            "hates": [
                "Analogies that miss technical nuance",
                "Marketing language dressed as engineering insight",
                "Lists of tools without context on when to use them",
                "Anything that starts with 'AI is changing the world'",
                "Content that treats them like a non-technical audience",
            ],
            "format": "Dense technical, data-backed, with reasoning shown",
            "depth": "expert",
        },
        "trust_signals": [
            "Specific numbers: tokens, latency ms, cost per 1k calls",
            "Failure analysis with root cause — not just 'here's what worked'",
            "Benchmarks compared against alternatives with methodology",
            "Code that actually runs without hidden dependencies",
        ],
        "trust_breakers": [
            "Vague superlatives ('incredibly powerful')",
            "Analogies that don't hold under technical scrutiny",
            "Claiming something is 'simple' or 'just works'",
            "Ignoring tradeoffs",
        ],
        "emotional_triggers": [
            "Fear of shipping broken inference in production",
            "Pride in elegant system design under constraints",
            "Frustration with the hype vs. reality gap in AI",
            "Curiosity about approaches they haven't considered",
        ],
        "scroll_triggers": [
            "A specific production failure mode they've seen",
            "A performance number that seems too good to be true",
            "An architecture pattern they've never considered",
        ],
        "cta_preferences": [
            "Ask a specific technical question they'll have an opinion on",
            "Point to a benchmark, repo, or paper",
            "Invite technical debate or counterexamples",
        ],
    },

    "founder": {
        "id": "founder",
        "label": "Startup Founder / CEO",
        "aliases": [
            "founder", "startup founder", "ceo", "co-founder", "entrepreneur",
            "early stage", "seed stage", "bootstrapped", "operator",
        ],
        "knowledge_level": "strategic",
        "background": (
            "Building a company. Makes decisions with incomplete information. "
            "Reads widely but shallow. Cares about outcomes over implementations."
        ),
        "pain_points": [
            "Can't tell if they're building something people actually want",
            "Hiring — not enough signal to separate great from good candidates",
            "Investors want traction before giving capital to get traction",
            "First 10 customers came from network — next 10 are a black box",
            "The product is never as fast as the vision demands",
            "Market looks different from inside than from outside",
            "Isolation — no one around them truly understands the pressure",
        ],
        "vocabulary": {
            "use": [
                "traction", "signal", "distribution", "burn rate", "PMF",
                "unit economics", "CAC", "LTV", "churn", "runway",
                "conviction", "compounding", "leverage",
            ],
            "avoid": [
                "synergy", "disrupt", "revolutionize", "scalable solution",
                "best-in-class", "cutting-edge", "world-class team",
            ],
        },
        "content_preferences": {
            "wants": [
                "Hard-won lessons from people who've actually done it",
                "Mental models that simplify complex decisions under uncertainty",
                "Counterintuitive takes that challenge default startup thinking",
                "Tactical advice they can act on this week",
                "Honest acknowledgment of what didn't work",
            ],
            "hates": [
                "Generic startup advice ('talk to your customers', 'iterate fast')",
                "Success theater from people who haven't done the work",
                "VC-speak that sounds important but says nothing",
                "Long posts that take 800 words to make one point",
                "Advice that only works for well-funded companies",
            ],
            "format": "Short, punchy, one clear idea per piece",
            "depth": "moderate",
        },
        "trust_signals": [
            "Specific numbers from their own company or verified sources",
            "Admitting what went wrong before giving the lesson",
            "Referencing a specific moment of genuine uncertainty",
            "A take that risks disagreement",
        ],
        "trust_breakers": [
            "Bragging disguised as humility",
            "Advice from someone who's never shipped anything",
            "Generic lists without context",
            "Starting with 'I'm humbled to announce'",
        ],
        "emotional_triggers": [
            "Fear of getting distribution wrong after building something great",
            "Ambition that runs ahead of current execution capacity",
            "Imposter syndrome in rooms full of people who seem more certain",
            "Isolation from having information others don't",
        ],
        "scroll_triggers": [
            "A hard lesson that matches something they're living right now",
            "A contrarian take they haven't heard framed this way",
            "An uncomfortable truth about building companies",
        ],
        "cta_preferences": [
            "Ask what they're working on or what they'd do differently",
            "Invite them to share their version of the lesson",
            "Point to something that earns real attention, not just engagement",
        ],
    },

    "marketer": {
        "id": "marketer",
        "label": "Digital Marketer / Growth Professional",
        "aliases": [
            "marketer", "marketing", "growth", "content marketer", "digital marketer",
            "performance marketer", "brand manager", "demand gen", "growth hacker",
            "cmo", "vp marketing",
        ],
        "knowledge_level": "intermediate",
        "background": (
            "Manages campaigns, content, and conversion funnels. "
            "Lives by metrics. Balances creative quality with distribution scale."
        ),
        "pain_points": [
            "Content that doesn't convert despite high traffic",
            "Attribution is broken — can't prove which channel is working",
            "AI-generated content making SERPs and feeds generic",
            "Stakeholders want pipeline, not brand — hard to explain compounding",
            "Competing for attention in over-saturated channels",
            "Creative teams and data teams speak different languages",
            "B2B buying cycles too long to show fast ROI",
        ],
        "vocabulary": {
            "use": [
                "conversion rate", "CPL", "CAC", "MQL", "pipeline", "funnel",
                "engagement rate", "CTR", "A/B test", "attribution",
                "demand gen", "PLG", "inbound", "organic reach",
            ],
            "avoid": [
                "leverage synergies", "holistic approach", "360-degree view",
                "best-in-class", "omnichannel (without specifics)",
            ],
        },
        "content_preferences": {
            "wants": [
                "Specific campaign results with real numbers",
                "Frameworks they can apply to their own funnels this week",
                "Honest takes on what platforms are actually worth investing in",
                "Data that helps them win internal budget arguments",
                "Creative angles they haven't seen in their own industry",
            ],
            "hates": [
                "Vanity metrics dressed as success stories",
                "Advice without benchmarks or context",
                "Thought leadership without any actionable substance",
                "Anyone who says 'just make better content'",
                "Overly technical content disconnected from outcomes",
            ],
            "format": "Data-backed frameworks with clear, fast takeaways",
            "depth": "moderate",
        },
        "trust_signals": [
            "Specific campaign metrics: CTR, conversion rates, CPL",
            "Before/after results with the context that made them possible",
            "Industry benchmarks they can compare their numbers against",
            "Frameworks that simplify a decision they make regularly",
        ],
        "trust_breakers": [
            "Statistics without source or context",
            "Success stories that hide the messy middle",
            "Generic content strategy advice that ignores their constraints",
            "Anyone claiming a tactic 'always works'",
        ],
        "emotional_triggers": [
            "Fear of wasting budget on channels that don't convert",
            "Pressure to prove ROI to skeptical leadership",
            "Creative frustration when constrained by performance data",
            "FOMO on channels competitors are investing in",
        ],
        "scroll_triggers": [
            "A specific number they didn't think was achievable",
            "A contrarian take on a channel they're already invested in",
            "A campaign result they wish they could show their boss",
        ],
        "cta_preferences": [
            "Ask what their biggest distribution challenge is right now",
            "Invite them to share their own results or counterexample",
            "Point to a test they could run this week",
        ],
    },

    "developer": {
        "id": "developer",
        "label": "Software Developer / Engineer",
        "aliases": [
            "developer", "software engineer", "engineer", "programmer",
            "backend", "frontend", "full stack", "fullstack", "dev",
        ],
        "knowledge_level": "expert",
        "background": (
            "Builds software professionally. Values clean abstractions, "
            "good tooling, and code that doesn't create new problems. Allergic to hype."
        ),
        "pain_points": [
            "Technical debt that slows every new feature",
            "Documentation outdated the moment it's written",
            "Meetings that fracture the flow state needed for deep work",
            "Being asked to estimate timelines for inherently uncertain work",
            "Tools that create three new problems while solving one",
            "Code reviews that feel like personal attacks",
            "A field that moves faster than any individual can keep up with",
        ],
        "vocabulary": {
            "use": [
                "abstraction", "refactor", "edge case", "tradeoff", "coupling",
                "idempotent", "stateless", "interface", "API contract", "test coverage",
                "complexity", "performance", "maintainability",
            ],
            "avoid": [
                "10x developer", "rockstar", "ninja", "guru",
                "seamlessly integrates", "best-in-class tooling",
            ],
        },
        "content_preferences": {
            "wants": [
                "Code they can copy and actually run",
                "Honest tradeoffs between approaches, not just recommendations",
                "Failure stories with real root cause analysis",
                "Opinions that come from production experience",
                "Problems explained clearly before solutions are offered",
            ],
            "hates": [
                "Tutorial content that skips all the hard parts",
                "Tools pitched as magic without explaining the cost",
                "Content that treats them as a junior",
                "Posts that could've been a tweet",
                "Pseudocode that avoids the actual implementation",
            ],
            "format": "Concrete examples, real code, clear reasoning",
            "depth": "expert",
        },
        "trust_signals": [
            "Code that actually works, with proper error handling",
            "Acknowledgment of edge cases and limitations",
            "Specific version numbers and environment context",
            "Benchmarks with methodology and reproducible setup",
        ],
        "trust_breakers": [
            "Generic 'best practices' without the context that makes them best",
            "Pseudocode that skips all the difficult parts",
            "Claiming something is 'simple' when it clearly isn't",
            "Ignoring failure modes and edge cases",
        ],
        "emotional_triggers": [
            "Satisfaction of finding an elegant solution to a real constraint",
            "Frustration with badly-designed systems they're forced to live with",
            "Pride in craft — code that future-them will thank them for",
            "Fear of shipping a bug that makes it to production",
        ],
        "scroll_triggers": [
            "A specific bug or edge case they've hit themselves",
            "A performance optimization they haven't tried",
            "An architectural pattern that contradicts what they currently do",
        ],
        "cta_preferences": [
            "Ask what they would do differently in this situation",
            "Invite them to point out what you missed",
            "Link to the actual code or repo",
        ],
    },

    "student": {
        "id": "student",
        "label": "Student / Early Career Professional",
        "aliases": [
            "student", "bootcamp", "junior", "entry level", "early career",
            "beginner", "learning", "career changer", "self-taught",
        ],
        "knowledge_level": "beginner",
        "background": (
            "Learning actively, often without a clear roadmap. Motivated but overwhelmed. "
            "Tutorial-capable but struggling to build real things."
        ),
        "pain_points": [
            "Too many resources with no clear path between them",
            "Tutorial hell — can do exercises but can't build real projects",
            "Imposter syndrome around peers who seem to know more",
            "Can't tell which skills to prioritize",
            "Getting a first job requires experience they don't have yet",
            "Technology moves faster than anyone can learn comprehensively",
            "Portfolio projects that feel fake, not real-world meaningful",
        ],
        "vocabulary": {
            "use": [
                "step by step", "for example", "in practice", "think of it like",
                "start with", "foundation", "practical", "project",
            ],
            "avoid": [
                "obviously", "just", "simply", "everyone knows", "trivial",
                "as you know", "of course", "it goes without saying",
            ],
        },
        "content_preferences": {
            "wants": [
                "Clear paths with concrete, prioritized next steps",
                "Real projects they can build to show employers",
                "Honest takes on what actually matters for getting hired",
                "Permission to not know everything — and a roadmap anyway",
                "Specific advice for their stage, not generic encouragement",
            ],
            "hates": [
                "Gatekeeping dressed as advice",
                "Content that makes them feel further behind than they are",
                "Vague encouragement without practical direction",
                "Content that requires skills they don't have yet to understand",
                "Advice that forgets what it's like to be a beginner",
            ],
            "format": "Step-by-step with clear expectations and realistic timelines",
            "depth": "accessible",
        },
        "trust_signals": [
            "Someone who remembers what it felt like to be where they are",
            "Specific first steps they can take today",
            "Realistic timelines — not 'learn X in 30 days'",
            "Honest mistakes the writer made as a beginner",
        ],
        "trust_breakers": [
            "Skipping steps because they seem 'obvious'",
            "Making the learning curve sound steeper than necessary",
            "Overwhelming lists without prioritization",
            "Anyone who forgot what confusion feels like",
        ],
        "emotional_triggers": [
            "Hope that the career change is actually possible",
            "Fear of wasting time on the wrong skills",
            "Excitement about the first moment something clicks",
            "Anxiety about whether they're smart enough to make it",
        ],
        "scroll_triggers": [
            "A clear answer to 'where do I actually start?'",
            "Someone who admits they struggled exactly where the reader is",
            "A specific, achievable outcome they can see themselves reaching",
        ],
        "cta_preferences": [
            "Invite them to share where they are in their journey",
            "Point them to the single most important next step",
            "Ask what they're stuck on specifically",
        ],
    },

    "enterprise_buyer": {
        "id": "enterprise_buyer",
        "label": "Enterprise Decision Maker",
        "aliases": [
            "enterprise", "cto", "vp engineering", "vp technology",
            "director of engineering", "enterprise buyer", "b2b buyer",
            "procurement", "it director",
        ],
        "knowledge_level": "strategic",
        "background": (
            "Evaluates technology for large organizations. Risk-averse. "
            "Accountable to multiple stakeholders. Cares about security, compliance, and integration."
        ),
        "pain_points": [
            "Vendor lock-in that creates long-term dependencies",
            "Integration complexity that destroys projected ROI",
            "Security and compliance requirements few vendors truly meet",
            "Proving technology ROI to finance teams that don't understand it",
            "Change management — getting teams to adopt new tools at scale",
            "Vendors who overpromise and underdeliver after contract signing",
            "Hidden costs that appear after procurement is complete",
        ],
        "vocabulary": {
            "use": [
                "ROI", "TCO", "SLA", "compliance", "security posture",
                "scalability", "integration", "change management",
                "governance", "enterprise grade", "support tier",
            ],
            "avoid": [
                "disrupt", "move fast", "hack", "startup mentality",
                "we'll figure it out", "agile (used as a buzzword)",
            ],
        },
        "content_preferences": {
            "wants": [
                "Case studies from companies in their industry with specific outcomes",
                "Clear security, compliance, and data governance documentation",
                "Total cost of ownership, not just licensing fees",
                "Migration paths, implementation timelines, and support structures",
                "Reference customers they can speak with",
            ],
            "hates": [
                "Demos that don't reflect real production scenarios",
                "Vague claims about 'enterprise readiness'",
                "Founders who dismiss compliance concerns",
                "Content that treats enterprise decisions like consumer purchases",
                "Statistics without attribution or methodology",
            ],
            "format": "Structured, professional, evidence-based",
            "depth": "moderate to deep on specific risk areas",
        },
        "trust_signals": [
            "Named enterprise customers in their sector with specific outcomes",
            "Third-party security audits and compliance certifications",
            "SLAs with specific uptime and response guarantees",
            "Clear escalation paths and dedicated support structures",
        ],
        "trust_breakers": [
            "Vague security claims",
            "Case studies without specifics",
            "Inability to answer direct compliance questions",
            "Dismissing their concerns as over-engineering",
        ],
        "emotional_triggers": [
            "Fear of making a costly, visible mistake in front of the organization",
            "Pressure to modernize without disrupting current operations",
            "Desire to be seen as forward-thinking and strategic",
            "Risk aversion built from previous failed technology rollouts",
        ],
        "scroll_triggers": [
            "A case study from a company they know and respect",
            "A specific compliance question answered directly",
            "ROI data they could put in a board presentation",
        ],
        "cta_preferences": [
            "Invite them to a technical deep-dive or proof of concept",
            "Offer a reference call with an existing enterprise customer",
            "Provide a structured evaluation path with clear milestones",
        ],
    },

    "seo_expert": {
        "id": "seo_expert",
        "label": "SEO / Content Strategist",
        "aliases": [
            "seo", "seo expert", "search engine optimization", "content strategist",
            "organic growth", "content seo", "technical seo", "seo manager",
        ],
        "knowledge_level": "expert",
        "background": (
            "Understands search intent, keyword strategy, and content architecture at depth. "
            "Works with SERP data, Core Web Vitals, and content performance metrics daily."
        ),
        "pain_points": [
            "Google updates that invalidate months of work overnight",
            "Clients who want to rank in 30 days for highly competitive keywords",
            "Content teams that write for humans but ignore search intent entirely",
            "Technical SEO issues buried in development backlogs",
            "Attribution from organic to revenue is always undervalued",
            "AI content flooding SERPs with low-quality pages",
            "Stakeholders who measure SEO success by position, not revenue",
        ],
        "vocabulary": {
            "use": [
                "search intent", "SERP", "E-E-A-T", "featured snippet",
                "topical authority", "keyword cannibalization", "semantic SEO",
                "Core Web Vitals", "crawl budget", "internal linking",
                "backlink profile", "entity", "SGE",
            ],
            "avoid": [
                "keyword stuffing", "link schemes", "SEO tricks",
                "secret strategies", "guaranteed rankings",
            ],
        },
        "content_preferences": {
            "wants": [
                "Specific data from real campaigns with context",
                "Framework for evaluating search intent accurately",
                "Takes on how AI search (SGE) changes the content game",
                "Technical analysis of algorithm updates with evidence",
                "Case studies showing what actually moved organic metrics",
            ],
            "hates": [
                "Generic 'write quality content' advice",
                "Posts that could have been written in 2018",
                "Anyone who guarantees specific ranking positions",
                "Keyword-stuffed content that ranks for nothing",
                "SEO advice that ignores user experience",
            ],
            "format": "Data-backed, specific, technical depth when the topic demands it",
            "depth": "expert",
        },
        "trust_signals": [
            "Specific SERP data and traffic numbers from real campaigns",
            "Before/after organic traffic with context on what changed",
            "References to specific algorithm updates with evidence",
            "Tools and methodologies explained with reasoning",
        ],
        "trust_breakers": [
            "Outdated SEO advice presented as current",
            "Generic content strategy that ignores search intent",
            "Anyone using 'guaranteed' near ranking positions",
            "Ignoring the impact of algorithm updates",
        ],
        "emotional_triggers": [
            "Frustration with Google's constant, opaque rule changes",
            "Pride in organic as a sustainable, compounding channel",
            "Anxiety over ranking drops from algorithm updates",
            "Satisfaction from content that ranks and converts years later",
        ],
        "scroll_triggers": [
            "A data point from a campaign they haven't seen before",
            "A take on SGE/AI search they haven't fully processed",
            "A technical issue they recognize from their own properties",
        ],
        "cta_preferences": [
            "Ask what algorithm update has hurt them most and why",
            "Invite them to share their own case study or counterexample",
            "Point to a specific audit or tool they can apply immediately",
        ],
    },

    "general_professional": {
        "id": "general_professional",
        "label": "General Professional",
        "aliases": [],  # Fallback — matches anything that doesn't match above
        "knowledge_level": "intermediate",
        "background": "Works in a professional context. Intelligent, busy, and discerning.",
        "pain_points": [
            "Too much information, not enough genuine insight",
            "Generic advice that doesn't account for their specific context",
            "Content that wastes their time before delivering its value",
            "Lack of clear, actionable next steps",
        ],
        "vocabulary": {
            "use": ["clear", "practical", "specific", "actionable", "evidence-based"],
            "avoid": ["leverage", "synergy", "paradigm shift", "circle back", "net-net", "move the needle"],
        },
        "content_preferences": {
            "wants": [
                "Specific ideas they can apply to their actual situation",
                "Writing that respects their intelligence without assuming domain expertise",
                "Real examples, not hypotheticals or thought experiments",
                "Opinions backed by reasoning they can follow",
            ],
            "hates": [
                "Jargon used to sound smart rather than be precise",
                "Generic advice that could apply to everyone and therefore helps no one",
                "Padding and filler that buries the actual insight",
                "Vague calls to action that don't specify the next step",
            ],
            "format": "Clear, professional, appropriately concise",
            "depth": "moderate",
        },
        "trust_signals": [
            "Specificity and concrete real-world examples",
            "Claims that don't oversell",
            "Visible reasoning behind opinions",
        ],
        "trust_breakers": [
            "Vague superlatives",
            "Obvious claims dressed up as insights",
            "Generic advice with no situational context",
        ],
        "emotional_triggers": [
            "Desire to be competent, respected, and well-informed",
            "Fear of making a decision with incomplete information",
        ],
        "scroll_triggers": [
            "Something specific they haven't encountered framed this way",
            "A practical tool, framework, or decision model",
        ],
        "cta_preferences": [
            "Ask a specific, relevant question",
            "Offer one clear, concrete next step",
        ],
    },
}


def get_profile(audience: str) -> dict:
    """Match free-text audience description to the best-fit profile."""
    if not audience:
        return PROFILES["general_professional"]

    audience_lower = audience.lower()

    # Direct ID match
    if audience_lower in PROFILES:
        return PROFILES[audience_lower]

    # Alias matching (most specific profiles first, general last)
    ordered = [p for pid, p in PROFILES.items() if pid != "general_professional"]
    for profile in ordered:
        for alias in profile.get("aliases", []):
            if alias in audience_lower:
                return profile

    return PROFILES["general_professional"]


def list_profiles() -> list[str]:
    return [p["label"] for p in PROFILES.values()]


def list_profile_ids() -> list[str]:
    return list(PROFILES.keys())
