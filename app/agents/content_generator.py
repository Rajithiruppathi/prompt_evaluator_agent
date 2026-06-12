"""
Stage 5 — Content Generation

Calls the LLM with the optimized prompt. Stateless — receives the prompt,
returns the generated content. No business logic here.

When MOCK_MODE=true no LLM call is made — a deterministic fake response is
returned instead so the full pipeline can be exercised without API keys.
"""

from app.core.llm import generator_llm
from app.core.config import MOCK_MODE

import logging

logger = logging.getLogger(__name__)


def _mock_generate(prompt: str, use_case: str, style: str) -> str:
    """Deterministic fake content for MOCK_MODE. No LLM call. No API key required."""
    first_line = prompt.splitlines()[0].strip()[:120] if prompt.strip() else "AI content generation"
    return (
        f"MOCK GENERATED CONTENT: {first_line}\n\n"
        f"Most teams skip the fundamentals. They deploy an AI pipeline, celebrate "
        f"the demo, and discover three months later that the outputs are inconsistent, "
        f"the costs are unpredictable, and users stopped trusting the results.\n\n"
        f"The pattern is always the same. Fast prototype. Real-world failure. "
        f"Painful redesign.\n\n"
        f"What actually works is validation at every layer: intent detection before "
        f"generation, quality scoring before delivery, and repair loops that know "
        f"when to stop. Not because the theory is elegant — but because production "
        f"data is messier than any eval set.\n\n"
        f"Platform: {use_case or 'general'} | Style: {style or 'none'} | "
        f"Set MOCK_MODE=false to use a real LLM."
    )


def generate(prompt: str, use_case: str = "", style: str = "") -> str:
    """
    Generate content from the optimized prompt.

    Args:
        prompt:   The fully assembled generation prompt from prompt_optimizer.
        use_case: Platform context (for logging only).
        style:    Writing style (for logging only).

    Returns:
        Raw generated content string.
    """
    if not prompt.strip():
        logger.warning("generate() called with empty prompt — returning empty string")
        return ""

    if MOCK_MODE:
        logger.info("[MOCK MODE ENABLED] Skipping LLM call — returning deterministic mock content")
        return _mock_generate(prompt, use_case, style)

    logger.info(f"Generating | use_case={use_case} | style={style or 'none'}")

    llm = generator_llm()
    response = llm.invoke(prompt)
    content = str(response.content).strip()

    logger.info(f"Generated | {len(content)} chars | {len(content.split())} words")
    return content
