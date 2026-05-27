"""
Stage 4 — Prompt Optimization

Delegates to the context engineering layer: build_context() assembles a
ContextPackage from all platform/audience/style/example/failure inputs,
then ContextPackage.to_prompt() serializes it to a compact structured prompt.

No LLM call here — pure composition.
"""

from app.context.context_builder import build_context, ContextPackage


def build_generation_prompt_with_context(
    topic: str,
    intent: str,
    audience: str,
    use_case: str,
    style: str = "",
    existing_content: str = "",
    target_use_case: str = "",
    feedback: str = "",
    experience_block: str = "",
    entropy_block: str = "",
    memory_directive: str = "",
) -> tuple[str, ContextPackage]:
    """
    Assemble a ContextPackage and serialize it to the generation prompt.

    Returns:
        (prompt_str, context_package) — prompt for the LLM; package for
        pre-generation validation and post-generation failure recording.
    """
    ctx = build_context(
        topic=topic,
        use_case=use_case,
        audience=audience,
        style=style,
        intent=intent,
        existing_content=existing_content,
        target_use_case=target_use_case,
        feedback=feedback,
        experience_block=experience_block,
        entropy_block=entropy_block,
        memory_directive=memory_directive,
    )
    return ctx.to_prompt(), ctx
