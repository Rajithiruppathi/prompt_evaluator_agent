"""
API Routes — all endpoints for the content generation system.

Endpoints:
  POST /generate   → Full 8-stage pipeline
  POST /validate   → Validate existing content
  GET  /styles     → Available writing styles
  GET  /platforms  → Supported platforms / use cases
  GET  /audiences  → Supported audience profiles
  GET  /health     → Health check
"""

from fastapi import APIRouter, HTTPException

from app.schemas.request  import ContentRequest, ValidateRequest
from app.schemas.response import ContentResponse, ValidateResponse  # noqa: F401
from app.workflows.content_workflow import run as run_workflow
from app.agents.validator import validate
from app.knowledge.styles.profiles    import list_styles
from app.knowledge.platforms.profiles import list_platforms
from app.knowledge.audiences.profiles import list_profiles

import logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=ContentResponse)
def generate(request: ContentRequest) -> ContentResponse:
    """
    Full 8-stage content generation pipeline.

    Handles:
    - Creating new content from a topic
    - Improving existing prompts or content
    - Rewriting existing content
    - Converting content between platforms

    Automatically detects intent if not specified.
    """
    logger.info(
        f"[/generate] use_case={request.use_case} | audience={request.audience} | "
        f"intent={request.intent or 'auto'} | style={request.style or 'none'}"
    )
    try:
        return run_workflow(request)
    except Exception as e:
        logger.error(f"[/generate] Pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidateResponse)
def validate_content(request: ValidateRequest) -> ValidateResponse:
    """
    Validate existing content against the quality framework.

    Returns a score 0-100, grade, and a structured list of failures and warnings.
    Useful for auditing existing content before publishing.
    """
    from app.knowledge.platforms.profiles import get_profile
    platform = get_profile(request.use_case)
    ctx = {"platform": platform, "use_case": request.use_case}
    result = validate(request.content, ctx)
    return ValidateResponse(
        score=result.score,
        grade=result.grade,
        recommendation=result.summary,
        failures=result.failures,
        warnings=result.warnings,
        passed=result.passed,
    )


@router.get("/styles")
def get_styles():
    """List all available writing style identities."""
    return {"styles": list_styles()}


@router.get("/platforms")
def get_platforms():
    """List all supported platforms / use cases."""
    return {"platforms": list_platforms()}


@router.get("/audiences")
def get_audiences():
    """List all supported audience profiles."""
    return {"audiences": list_profiles()}


@router.get("/use-cases")
def get_use_cases():
    """Alias for /platforms — backwards compatible."""
    return {"use_cases": list_platforms()}
