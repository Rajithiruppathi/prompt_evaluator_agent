"""
Quality reference examples — hooks, CTAs, and anti-patterns per platform.

These are not injected into generation prompts (which would create dependency on examples).
They serve as:
  - Calibration references for validation scoring
  - Training material for understanding quality bar
  - Documentation for humans extending the system
"""

HOOK_EXAMPLES: dict[str, dict] = {
    "linkedin_post": {
        "strong": [
            "We hired 4 engineers in 90 days with zero agency fees. Here's what actually worked.",
            "I turned down a $2M acquisition offer. Three years later, I know I made the right call.",
            "Most RAG pipelines hallucinate on 30% of queries. Nobody talks about why.",
            "Cold outreach open rates dropped 40% this year. These two changes got ours back to 62%.",
        ],
        "weak": [
            "In today's fast-paced world, AI is changing everything.",
            "I am excited to share that our team has achieved incredible results.",
            "Hiring is one of the most important things founders do.",
            "Networking is key to success in the modern workplace.",
        ],
    },
    "cold_email": {
        "strong": [
            "Saw your post about scaling the data team — we solved the same bottleneck at Stripe.",
            "Your pipeline tracking setup looks manual. We automated ours in 3 hours.",
            "One thing I noticed on your site: your checkout flow has the same drop-off pattern we fixed for Notion.",
        ],
        "weak": [
            "I hope this email finds you well.",
            "My name is [Name] and I work at [Company].",
            "I wanted to reach out because I think our product could be a great fit for your company.",
        ],
    },
    "blog": {
        "strong": [
            "Every developer I know has made the same mistake with async/await. Including me, twice.",
            "We A/B tested 12 headlines over 6 months. The results contradicted everything we thought we knew.",
        ],
        "weak": [
            "In today's digital age, content marketing has become increasingly important.",
            "If you're looking to improve your SEO, you've come to the right place.",
        ],
    },
}

CTA_EXAMPLES: dict[str, dict] = {
    "linkedin_post": {
        "strong": [
            "What's the most counterintuitive thing you've learned about hiring?",
            "Has this happened to you? What did you do differently?",
            "Disagree? Tell me what I'm missing.",
        ],
        "weak": [
            "What do you think? Let me know in the comments!",
            "Share if you agree!",
            "Follow me for more content like this.",
        ],
    },
    "cold_email": {
        "strong": [
            "Worth a 15-minute call Thursday or Friday?",
            "Would it make sense to show you how we did it?",
            "Can I send you the one-pager?",
        ],
        "weak": [
            "Feel free to reach out if you have any questions.",
            "Let me know if you'd like to learn more.",
            "Looking forward to hearing from you!",
        ],
    },
}

AI_CLICHES: list[str] = [
    "leverage", "dive deep", "game-changer", "paradigm shift", "synergy",
    "unlock", "cutting-edge", "revolutionize", "disrupt", "seamlessly",
    "holistic", "robust", "empower", "scalable", "innovative",
    "best-in-class", "world-class", "next-generation", "transformative",
    "unprecedented", "unparalleled", "state-of-the-art", "groundbreaking",
    "in today's fast-paced", "in today's digital", "in today's world",
    "the future of", "at the end of the day", "it goes without saying",
    "needless to say", "it is what it is", "move the needle",
    "circle back", "low-hanging fruit", "boil the ocean",
    "think outside the box", "touch base",
    "going forward", "drill down", "take it to the next level",
    "value-add", "win-win", "pain point", "bandwidth", "ecosystem",
    "deep dive", "pivot", "actionable insights", "thought leadership",
    "best practices", "ideate", "learnings",
]

GENERIC_PHRASES: list[str] = [
    "it is important to note", "it is worth mentioning", "it goes without saying",
    "there are many ways", "there are several", "many people",
    "more and more", "increasingly important", "has become essential",
    "in today's competitive", "in today's digital", "plays a crucial role",
    "plays an important role", "in the realm of", "in the field of",
]

FAKE_STAT_PATTERNS: list[str] = [
    "studies show", "research shows", "research suggests",
    "according to studies", "according to research",
    "experts say", "experts believe", "it is widely known",
    "most people", "the majority of people", "many experts",
]
