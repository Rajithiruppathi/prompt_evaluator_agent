from typing import Optional, Literal
from pydantic import BaseModel, Field


class ValidationFailure(BaseModel):
    check: str = Field(description="Name of the validation check that failed")
    severity: Literal["critical", "high", "medium", "low"]
    message: str = Field(description="What was detected")
    suggestion: str = Field(description="How to fix it")
    auto_repaired: bool = Field(default=False, description="Whether the repair engine fixed this")


class ValidationResult(BaseModel):
    score: int = Field(description="Quality score 0-100. Higher is better.")
    grade: Literal["excellent", "good", "fair", "poor"]
    passed: list[str] = Field(description="Names of checks that passed")
    failures: list[ValidationFailure] = Field(description="High/critical failures")
    warnings: list[ValidationFailure] = Field(description="Medium/low issues")
    summary: str = Field(description="One-line editorial direction")


class HumanizationResult(BaseModel):
    """Four-dimension score for human authenticity. Produced by Stage 5b."""
    score: int = Field(description="Composite humanization score 0-100")
    grade: Literal["human", "borderline", "robotic"]
    specificity_score: int = Field(description="0-25: concrete numbers, tools, timeframes")
    tension_score: int = Field(description="0-25: conflict, failure, narrative reversal")
    originality_score: int = Field(description="0-25: absence of clichés and robotic transitions")
    experience_score: int = Field(description="0-25: practitioner-derived signals")
    issues: list[str] = Field(default_factory=list, description="Detected humanization problems")
    suggestions: list[str] = Field(default_factory=list, description="How to raise the score")


class PipelineStage(BaseModel):
    stage: str
    status: Literal["completed", "skipped", "failed"]
    detail: str


class ContentResponse(BaseModel):
    # Intent and context
    intent: str = Field(description="Detected or specified intent")
    use_case: str
    audience: str
    audience_profile: str = Field(description="Matched audience profile ID")
    style: Optional[str]
    tone: str

    # Content outputs
    optimized_prompt: str = Field(description="The enriched prompt sent to the LLM")
    draft_output: str = Field(description="Raw generated content before repair")
    final_output: str = Field(description="Final content after repair and formatting")

    # Quality
    validation: ValidationResult
    humanization: HumanizationResult = Field(description="Human-authenticity score across 4 dimensions")
    repaired: bool = Field(description="Whether the repair engine modified the output")

    # Pipeline trace
    pipeline: list[PipelineStage] = Field(description="Execution trace through all pipeline stages")

    # Metadata
    metadata: dict = Field(description="Platform profile, style, routing, and quality metadata")


class ValidateResponse(BaseModel):
    score: int
    grade: str
    recommendation: str
    failures: list[ValidationFailure]
    warnings: list[ValidationFailure]
    passed: list[str]
