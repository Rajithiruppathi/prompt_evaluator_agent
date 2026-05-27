"""
Reusable prompt composition primitives.
All agent prompt-building functions use these to maintain consistent structure.
"""


def section(title: str, body: str) -> str:
    return f"--- {title} ---\n{body}"


def bullet_list(items: list[str], prefix: str = "  •") -> str:
    return "\n".join(f"{prefix} {item}" for item in items if item)


def check_list(items: list[str]) -> str:
    return "\n".join(f"  ✓ {item}" for item in items if item)


def cross_list(items: list[str]) -> str:
    return "\n".join(f"  ✗ {item}" for item in items if item)


def forbidden_phrases(phrases: list[str], n: int = 15) -> str:
    sample = ", ".join(f'"{p}"' for p in phrases[:n])
    return f"FORBIDDEN PHRASES — never use any of these:\n{sample}\n...and anything that sounds assembled from a template."


def assemble(*sections: str) -> str:
    """Join non-empty sections with a separator."""
    return "\n\n---\n\n".join(s for s in sections if s.strip())
