"""
Stage 2 — Audience Intelligence

Matches a free-text audience description to a rich audience profile and returns
structured context that informs prompt construction, validation, and repair.
"""

from app.knowledge.audiences.profiles import get_profile


def build_audience_context(audience: str) -> dict:
    """
    Match the audience description to a profile and return structured context.

    Returns a dict with:
      - profile:           full profile dict
      - label:             human-readable name
      - knowledge_level:   expert | intermediate | beginner | strategic | accessible
      - pain_points:       list of specific pain points
      - vocabulary:        {use: [...], avoid: [...]}
      - trust_signals:     list of what earns trust
      - trust_breakers:    list of what breaks trust
      - content_prefs:     what they want and hate
      - scroll_triggers:   what makes them stop scrolling
      - cta_preferences:   what CTA styles work for them
    """
    profile = get_profile(audience)

    return {
        "profile":         profile,
        "label":           profile["label"],
        "knowledge_level": profile["knowledge_level"],
        "pain_points":     profile.get("pain_points", []),
        "vocabulary":      profile.get("vocabulary", {"use": [], "avoid": []}),
        "trust_signals":   profile.get("trust_signals", []),
        "trust_breakers":  profile.get("trust_breakers", []),
        "content_prefs":   profile.get("content_preferences", {}),
        "scroll_triggers": profile.get("scroll_triggers", []),
        "cta_preferences": profile.get("cta_preferences", []),
        "emotional_triggers": profile.get("emotional_triggers", []),
    }


