"""
Stage 5 — Content Generation

Calls the LLM with the optimized prompt. Stateless — receives the prompt,
returns the generated content. No business logic here.
"""

from app.core.llm import generator_llm

import logging

logger = logging.getLogger(__name__)


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

    logger.info(f"Generating | use_case={use_case} | style={style or 'none'}")

    llm = generator_llm()
    response = llm.invoke(prompt)
    content = str(response.content).strip()

    logger.info(f"Generated | {len(content)} chars | {len(content.split())} words")
    return content
