"""
Stage 3 — Use Case Strategy

Combines platform rules and style profile into a unified content strategy.
The strategy guides the prompt optimizer and validates the final output.
"""

from app.knowledge.platforms.profiles import get_profile as get_platform
from app.knowledge.styles.profiles import get_profile as get_style


def build_strategy(
    use_case: str,
    audience_context: dict,
    goal: str,
    tone: str,
    style: str = "",
) -> dict:
    """
    Build a content strategy from platform rules + style + audience context.

    Returns:
      - platform:         full platform profile
      - style:            style profile (empty dict if no style specified)
      - hook_direction:   recommended hook approach for this platform
      - structure:        ordered list of content sections
      - length_target:    optimal word count
      - cta_direction:    recommended CTA type
      - formatting_rules: structural requirements from platform profile
      - avoid:            failure conditions to avoid
    """
    platform = get_platform(use_case)
    style_profile = get_style(style) if style else {}

    hook_options = platform.get("hook_rules", {}).get("what_works", [])
    cta_options  = platform.get("cta_rules",  {}).get("strong", [])

    # If style specifies a hook pattern, it takes priority over platform default
    hook_direction = (
        style_profile.get("hook_pattern", hook_options[0] if hook_options else "")
        if style_profile and style_profile.get("hook_pattern")
        else (hook_options[0] if hook_options else "Lead with a specific, relevant opener")
    )

    return {
        "platform":         platform,
        "style":            style_profile,
        "hook_direction":   hook_direction,
        "structure":        platform.get("format", {}).get("sections", ["hook", "body", "cta"]),
        "length_target":    platform.get("format", {}).get("optimal_words", 300),
        "cta_direction":    cta_options[0] if cta_options else "Ask a specific, relevant question",
        "formatting_rules": platform.get("structural_requirements", {}),
        "avoid":            platform.get("failure_conditions", []),
        "tone_range":       platform.get("tone_range", []),
    }
