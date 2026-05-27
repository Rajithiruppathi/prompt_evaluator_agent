"""
Experience Pattern Library

Provides domain-specific production incident, tradeoff, and failure-mode patterns
that the prompt optimizer injects as narrative scaffolding.

These are structural suggestions — the LLM uses them to ground its writing in
the kind of specificity that only comes from actually having done the thing.
Not hallucinations; scaffold for earned realism.
"""

import random

_PATTERNS: list[dict] = [

    # AI / ML Engineering
    {
        "id": "latency_spike",
        "domains": ["ai_engineer", "developer"],
        "tension": "Inference latency was acceptable in testing but doubled under production load — not because of the model, but because the tokenizer was running on CPU while the GPU sat idle.",
        "observation": "The bottleneck is almost never where you measured it in staging.",
    },
    {
        "id": "retry_amplification",
        "domains": ["ai_engineer", "developer"],
        "tension": "Exponential backoff on rate limit errors turned a 10% failure rate into a traffic storm that hit every downstream service simultaneously.",
        "observation": "Retry logic that looks safe in isolation becomes an amplifier when every service applies it at the same time.",
    },
    {
        "id": "hallucination_edge_case",
        "domains": ["ai_engineer", "developer", "general"],
        "tension": "The model passed every benchmark but confidently fabricated a company name in production — one that appeared in exactly zero training examples.",
        "observation": "Benchmark performance is a ceiling estimate, not a floor guarantee.",
    },
    {
        "id": "token_explosion",
        "domains": ["ai_engineer", "developer"],
        "tension": "Context window limits forced a hard architectural choice: prompt compression (losing critical context) or chunking (losing coherence across chunk boundaries).",
        "observation": "Token limits reveal product decisions that were quietly deferred.",
    },
    {
        "id": "evaluation_failure",
        "domains": ["ai_engineer"],
        "tension": "The automated eval said quality improved 12%. Manual review showed the model had learned to pattern-match the rubric, not the actual task.",
        "observation": "When your eval is a proxy metric, optimizing for it is Goodhart's Law in action.",
    },
    {
        "id": "deployment_failure",
        "domains": ["ai_engineer", "developer"],
        "tension": "The canary deployment looked clean — until load scaled and the model ran out of GPU memory on the variant that hadn't been benchmarked at peak concurrency.",
        "observation": "What you test at 1x request rate doesn't predict behavior at 10x.",
    },
    {
        "id": "api_bottleneck",
        "domains": ["ai_engineer", "developer"],
        "tension": "Rate limits on the API were documented. The undocumented limit was concurrent requests — which only appeared at production scale, 6 weeks after launch.",
        "observation": "The API contract covers the happy path. Your architecture has to cover the rest.",
    },
    {
        "id": "memory_leak",
        "domains": ["developer", "ai_engineer"],
        "tension": "Memory climbed slowly over 72 hours, only crossing the alert threshold overnight. Root cause: a conversation history buffer that was never pruned.",
        "observation": "Resources that accumulate gradually are harder to attribute than resources that spike.",
    },
    {
        "id": "context_drift",
        "domains": ["ai_engineer"],
        "tension": "The model's responses degraded noticeably in long sessions. The issue wasn't model quality — earlier in the context window, a malformed tool response was poisoning all subsequent reasoning.",
        "observation": "Context quality degrades non-linearly. The first bad input affects everything after it.",
    },
    {
        "id": "prompt_injection",
        "domains": ["ai_engineer", "developer"],
        "tension": "User-provided content appeared in the system prompt via a template. A single malformed input restructured the model's behavior for the entire session.",
        "observation": "Anything that crosses the trust boundary into the prompt is an attack surface.",
    },

    # Startup / Founder
    {
        "id": "pivot_decision",
        "domains": ["founder"],
        "tension": "We had 90 days of runway and two signals pointing in opposite directions: users loved feature A, but only feature B had any revenue attached to it.",
        "observation": "The hardest product decisions are the ones where both options have real evidence behind them.",
    },
    {
        "id": "wrong_metric",
        "domains": ["founder", "marketer"],
        "tension": "We optimized for activation rate for six months. When we finally spoke to churned users, 80% had activated — they just never found the core value we assumed they had.",
        "observation": "You can hit every metric and still be measuring the wrong thing.",
    },
    {
        "id": "hiring_mistake",
        "domains": ["founder"],
        "tension": "The hire looked perfect — right skills, right experience, strong references. Three months in, the role had changed shape and we'd never updated what we were actually hiring for.",
        "observation": "Job descriptions are written for last quarter's problems.",
    },
    {
        "id": "pricing_discovery",
        "domains": ["founder", "marketer"],
        "tension": "We launched at $29/month because it felt approachable. A customer told us unprompted that at that price they assumed it wasn't serious software.",
        "observation": "Pricing sends a signal before the product can prove itself.",
    },
    {
        "id": "customer_discovery_failure",
        "domains": ["founder"],
        "tension": "We did 40 customer interviews. Everyone said they'd pay for it. We launched. Fourteen people converted, none of whom had been in any of the interviews.",
        "observation": "People in interviews are trying to be helpful. People at checkout are making real decisions.",
    },

    # Marketing / Content
    {
        "id": "copy_flat",
        "domains": ["marketer"],
        "tension": "The copy that tested best internally was the one the team thought was too blunt. The polished version had 3x more words and half the click rate.",
        "observation": "Marketing copy optimized for internal approval rarely survives contact with the actual audience.",
    },
    {
        "id": "campaign_failure",
        "domains": ["marketer"],
        "tension": "The campaign had the right message but launched into the wrong channel — the audience was on LinkedIn, but the budget was split evenly with Instagram.",
        "observation": "Message-channel fit matters as much as message-market fit.",
    },
    {
        "id": "seo_trap",
        "domains": ["marketer", "seo_expert"],
        "tension": "The article ranked on page one and drove 40,000 visits a month. None of them converted — the search intent was informational and the page asked for a credit card.",
        "observation": "Traffic without intent alignment is an expensive vanity metric.",
    },
    {
        "id": "attribution_failure",
        "domains": ["marketer"],
        "tension": "We cut the channel that showed zero last-touch attribution. Three months later, pipeline dropped 30%. The channel had been responsible for first-touch on half of our enterprise deals.",
        "observation": "Last-touch attribution systematically undervalues the top of the funnel.",
    },

    # Enterprise / B2B
    {
        "id": "stakeholder_blindspot",
        "domains": ["enterprise_buyer"],
        "tension": "Procurement approved the tool. Three months later we discovered the team who'd actually use it had been in parallel talks with a different vendor the whole time.",
        "observation": "Buying authority and decision authority are not always the same person.",
    },
    {
        "id": "integration_surprise",
        "domains": ["enterprise_buyer", "developer"],
        "tension": "The vendor's integration docs were accurate. What they didn't document was the SSO configuration that required a separate enterprise tier — discovered after procurement had closed.",
        "observation": "The hidden costs in enterprise software live in the integration layer.",
    },

    # General / Cross-domain
    {
        "id": "documentation_gap",
        "domains": ["developer", "ai_engineer", "general"],
        "tension": "The docs covered the simple case perfectly. The production case — multi-tenancy with custom auth — required reading three GitHub issues and one Stack Overflow answer from 2021.",
        "observation": "Documentation coverage is inversely correlated with complexity at the edges.",
    },
    {
        "id": "assumption_failure",
        "domains": ["general", "founder", "developer"],
        "tension": "We built the feature based on what users said they wanted in the survey. When we shipped it, usage was near zero — because what they described and what they'd actually use were different things.",
        "observation": "Survey responses are aspirational. Usage data is honest.",
    },
    {
        "id": "deadline_tradeoff",
        "domains": ["developer", "founder", "general"],
        "tension": "We shipped on time by cutting error handling for edge cases. Six months later, one of those edge cases was 40% of production traffic.",
        "observation": "Edge cases in software have a way of becoming core cases over time.",
    },
    {
        "id": "dependency_surprise",
        "domains": ["developer", "ai_engineer"],
        "tension": "A transitive dependency updated a minor version. Three services broke in production because none of us had pinned anything below the direct dependency.",
        "observation": "You own your entire dependency tree, not just the packages you import directly.",
    },
]

_PROFILE_TO_DOMAIN: dict[str, list[str]] = {
    "ai_engineer":          ["ai_engineer", "developer", "general"],
    "startup_founder":      ["founder", "developer", "general"],
    "marketer":             ["marketer", "general"],
    "developer":            ["developer", "ai_engineer", "general"],
    "student":              ["general"],
    "enterprise_buyer":     ["enterprise_buyer", "general"],
    "seo_expert":           ["seo_expert", "marketer", "general"],
    "general_professional": ["general"],
}


def select_patterns(
    audience_profile: dict,
    use_case: str = "",
    n: int = 2,
) -> list[dict]:
    """
    Return n experience patterns relevant to the audience profile.

    Randomly sampled per request to prevent template repetition across calls.
    """
    profile_id = audience_profile.get("id", "general_professional")
    domains = _PROFILE_TO_DOMAIN.get(profile_id, ["general"])

    relevant = [p for p in _PATTERNS if any(d in p["domains"] for d in domains)]
    if not relevant:
        relevant = _PATTERNS

    count = min(n, len(relevant))
    return random.sample(relevant, count)


def format_for_prompt(patterns: list[dict]) -> str:
    """
    Format selected patterns as a prompt injection block.

    The LLM is instructed to use these as structural inspiration —
    not to copy them verbatim.
    """
    if not patterns:
        return ""

    lines = [
        "Draw specificity from patterns like these (use as structural inspiration — "
        "do not copy verbatim; adapt or use a parallel scenario from your own training):\n"
    ]
    for p in patterns:
        lines.append(f"  Tension: {p['tension']}")
        lines.append(f"  Observation: {p['observation']}\n")

    return "\n".join(lines)
