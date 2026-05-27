"""
Stage 8 — Final Response Formatter

Applies platform-native formatting to the final content after repair.
This is the last step before returning to the user.

Formatting fixes structural issues that can be corrected deterministically:
  - Hashtag positioning (LinkedIn: always at the end)
  - Paragraph spacing
  - Trailing whitespace
  - Line break normalization

Does NOT rewrite content — that's the repair engine's job.
"""

import re


def format_output(content: str, use_case: str, platform: dict) -> str:
    """
    Apply final platform-specific formatting to content.
    Returns cleaned, properly structured content.
    """
    if not content.strip():
        return content

    use_case_lower = use_case.lower()

    # Apply platform-specific formatter
    if "linkedin" in use_case_lower:
        content = _format_linkedin(content, platform)
    elif "blog" in use_case_lower or "article" in use_case_lower or "seo" in use_case_lower:
        content = _format_blog(content)
    elif "email" in use_case_lower:
        content = _format_email(content)
    elif "twitter" in use_case_lower or "thread" in use_case_lower:
        content = _format_twitter_thread(content)
    else:
        content = _format_general(content)

    return content.strip()


def _format_linkedin(content: str, platform: dict) -> str:
    """Ensure LinkedIn formatting: hashtags at end, proper paragraph breaks."""
    lines = content.split("\n")

    # Separate hashtag lines from body lines
    hashtag_lines = [l.strip() for l in lines if _is_hashtag_line(l)]
    body_lines    = [l for l in lines if not _is_hashtag_line(l)]

    # Clean up body
    body = "\n".join(body_lines).strip()
    body = _normalize_paragraph_spacing(body)

    # Ensure hashtags are at the end
    if hashtag_lines:
        hashtags = " ".join(hashtag_lines)
        return f"{body}\n\n{hashtags}"

    # If no hashtags found, check for inline hashtags and leave them
    return body


def _format_blog(content: str) -> str:
    """Normalize blog formatting: consistent heading style, paragraph spacing."""
    content = _normalize_paragraph_spacing(content)
    # Normalize heading spacing: ensure blank line before each heading
    content = re.sub(r"([^\n])\n(#{1,3} )", r"\1\n\n\2", content)
    return content


def _format_email(content: str) -> str:
    """Normalize email formatting: clean paragraph spacing, no double blanks."""
    return _normalize_paragraph_spacing(content)


def _format_twitter_thread(content: str) -> str:
    """Ensure tweet numbering is consistent."""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    numbered = []

    for i, para in enumerate(paragraphs, 1):
        # Don't double-number if already has a number
        if not re.match(r"^\d+/", para):
            para = f"{i}/ {para}"
        numbered.append(para)

    return "\n\n".join(numbered)


def _format_general(content: str) -> str:
    return _normalize_paragraph_spacing(content)


def _is_hashtag_line(line: str) -> bool:
    """Return True if the line consists only of hashtags."""
    stripped = line.strip()
    if not stripped:
        return False
    words = stripped.split()
    return all(w.startswith("#") for w in words)


def _normalize_paragraph_spacing(content: str) -> str:
    """Replace 3+ newlines with exactly 2, clean trailing whitespace per line."""
    lines = [l.rstrip() for l in content.split("\n")]
    content = "\n".join(lines)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content
