"""
Context Engineering Package

Provides typed, composable context objects that replace monolithic prompt strings.
Each context object knows how to represent itself compactly in a prompt.

Public API:
  build_context(...)        → ContextPackage   (primary entry point)
  ContextPackage.to_prompt()                    (compact structured prompt)

Pre-built context objects:
  Platform:  LinkedInContext, BlogContext, ColdEmailContext, AdCopyContext, ...
  Audience:  EngineerAudienceContext, FounderAudienceContext, ...
  Style:     ContraryExpertStyle, FounderStorytellerStyle, ...

Extension interfaces (for future RAG/memory/retrieval):
  ContextRetriever, StyleFingerprint, MemoryStore
"""

from app.context.context_builder import (
    build_context,
    ContextPackage,
    ContextRetriever,
    StyleFingerprint,
    MemoryStore,
)
from app.context.platform_context import (
    PlatformContext,
    LinkedInContext,
    BlogContext,
    ColdEmailContext,
    AdCopyContext,
    TwitterThreadContext,
    SEOArticleContext,
    TechnicalPostContext,
    EducationalContext,
    get_platform_context,
)
from app.context.audience_context import (
    AudienceContext,
    EngineerAudienceContext,
    FounderAudienceContext,
    MarketerAudienceContext,
    DeveloperAudienceContext,
    StudentAudienceContext,
    EnterpriseBuyerContext,
    SEOExpertContext,
    GeneralProfessionalContext,
    get_audience_context,
)
from app.context.style_context import (
    StyleContext,
    TechnicalEducatorStyle,
    ContraryExpertStyle,
    FounderStorytellerStyle,
    MinimalistOperatorStyle,
    StrategicAdvisorStyle,
    StorytellerStyle,
    AnalystStyle,
    get_style_context,
)
from app.context.examples_context import (
    ContentExample,
    get_examples,
)
from app.context.failure_memory import (
    FailureRecord,
    FailureMemory,
    record as record_failure,
    get_failure_context,
    get_recent as get_recent_failures,
    clear as clear_failures,
)
from app.context.banned_phrases import (
    get_banned,
    validate_content as validate_banned,
    format_for_prompt as format_banned_for_prompt,
)

__all__ = [
    "build_context",
    "ContextPackage",
    "ContextRetriever",
    "StyleFingerprint",
    "MemoryStore",
    "PlatformContext",
    "LinkedInContext",
    "BlogContext",
    "ColdEmailContext",
    "AdCopyContext",
    "TwitterThreadContext",
    "SEOArticleContext",
    "TechnicalPostContext",
    "EducationalContext",
    "get_platform_context",
    "AudienceContext",
    "EngineerAudienceContext",
    "FounderAudienceContext",
    "MarketerAudienceContext",
    "DeveloperAudienceContext",
    "StudentAudienceContext",
    "EnterpriseBuyerContext",
    "SEOExpertContext",
    "GeneralProfessionalContext",
    "get_audience_context",
    "StyleContext",
    "TechnicalEducatorStyle",
    "ContraryExpertStyle",
    "FounderStorytellerStyle",
    "MinimalistOperatorStyle",
    "StrategicAdvisorStyle",
    "StorytellerStyle",
    "AnalystStyle",
    "get_style_context",
    "ContentExample",
    "get_examples",
    "FailureRecord",
    "FailureMemory",
    "record_failure",
    "get_failure_context",
    "get_recent_failures",
    "clear_failures",
    "get_banned",
    "validate_banned",
    "format_banned_for_prompt",
]
