from typing import Optional, Literal
from pydantic import BaseModel, Field


class ContentRequest(BaseModel):
    """
    Unified request schema for all content operations.
    The system auto-detects intent from the prompt if not explicitly set.
    """

    # Core inputs — always required
    prompt: str = Field(
        ...,
        min_length=3,
        description=(
            "The topic to write about, existing content to improve, "
            "or a prompt to optimize. Context determines how it's interpreted."
        ),
    )
    use_case: str = Field(
        ...,
        description=(
            "Target platform or format. Examples: LinkedIn Post, Blog, Cold Email, "
            "Ad Copy, Twitter Thread, SEO Article, Technical Post."
        ),
    )
    audience: str = Field(
        ...,
        description="Target audience. e.g. 'AI Engineers', 'Startup Founders', 'Students'.",
    )
    goal: str = Field(
        ...,
        description="What this content should achieve. e.g. 'Drive engagement', 'Generate leads'.",
    )

    # Optional context
    tone: str = Field(
        default="Professional",
        description="Tone: Professional | Direct | Conversational | Casual | Persuasive | Technical.",
    )
    style: Optional[str] = Field(
        default=None,
        description=(
            "Writing style identity. Options: Technical Educator, Contrarian Expert, "
            "Founder Storyteller, Minimalist Operator, Strategic Advisor, Storyteller, Analyst."
        ),
    )

    # Intent — auto-detected if omitted
    intent: Optional[Literal["create", "improve", "rewrite", "convert"]] = Field(
        default=None,
        description=(
            "Content operation to perform. Auto-detected from prompt if not specified. "
            "'create': write new content. 'improve': enhance existing. "
            "'rewrite': full rewrite preserving core idea. 'convert': change platform/format."
        ),
    )

    # For improvement / rewrite / convert modes
    existing_content: Optional[str] = Field(
        default=None,
        description="Existing content when intent is 'improve', 'rewrite', or 'convert'.",
    )
    target_use_case: Optional[str] = Field(
        default=None,
        description="Target format when intent is 'convert'. e.g. 'Cold Email' when converting from 'Blog'.",
    )


class ValidateRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to validate")
    use_case: str = Field(default="", description="Optional platform context for validation")
