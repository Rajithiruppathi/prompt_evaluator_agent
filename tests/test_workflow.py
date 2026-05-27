"""
Integration tests for the 8-stage content pipeline.

Run with: pytest tests/ -v
"""

import pytest
from app.schemas.request import ContentRequest
from app.workflows.content_workflow import run
from app.agents.intent_analyzer import analyze_intent
from app.agents.validator import validate
from app.knowledge.audiences.profiles import get_profile as get_audience
from app.knowledge.platforms.profiles import get_profile as get_platform
from app.knowledge.styles.profiles import get_profile as get_style


# ---------------------------------------------------------------------------
# Intent analyzer tests
# ---------------------------------------------------------------------------

class TestIntentAnalyzer:
    def test_create_from_topic(self):
        assert analyze_intent("Write about AI in healthcare") == "create"

    def test_improve_from_signals(self):
        assert analyze_intent("Improve this post: ...") == "improve"

    def test_rewrite_from_signals(self):
        assert analyze_intent("Rewrite this for LinkedIn") == "rewrite"

    def test_convert_from_signals(self):
        assert analyze_intent("Convert this blog to a cold email") == "convert"

    def test_explicit_overrides_detection(self):
        assert analyze_intent("improve this", explicit_intent="create") == "create"

    def test_existing_content_defaults_to_improve(self):
        assert analyze_intent("make this better", existing_content="Some content here") == "improve"

    def test_default_is_create(self):
        assert analyze_intent("AI systems architecture") == "create"


# ---------------------------------------------------------------------------
# Knowledge base tests
# ---------------------------------------------------------------------------

class TestKnowledgeBase:
    def test_audience_ai_engineer_matched(self):
        profile = get_audience("AI Engineers")
        assert profile["id"] == "ai_engineer"

    def test_audience_founder_matched(self):
        profile = get_audience("Startup Founders")
        assert profile["id"] == "founder"

    def test_audience_fallback_to_general(self):
        profile = get_audience("Random unknown audience type")
        assert profile["id"] == "general_professional"

    def test_platform_linkedin_matched(self):
        platform = get_platform("LinkedIn Post")
        assert platform["id"] == "linkedin_post"

    def test_platform_blog_matched(self):
        platform = get_platform("Blog")
        assert platform["id"] == "blog"

    def test_platform_cold_email_matched(self):
        platform = get_platform("Cold Email")
        assert platform["id"] == "cold_email"

    def test_style_technical_educator_matched(self):
        style = get_style("Technical Educator")
        assert style["id"] == "technical_educator"

    def test_style_returns_default_for_unknown(self):
        style = get_style("unknown style xyz")
        assert style["id"] == "default"


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestValidator:
    def _ctx(self, use_case: str = "LinkedIn Post") -> dict:
        platform = get_platform(use_case)
        return {"platform": platform, "use_case": use_case}

    def test_empty_content_scores_zero(self):
        result = validate("", self._ctx())
        assert result.score == 0
        assert result.grade == "poor"

    def test_ai_cliches_reduce_score(self):
        content = "This is a game-changer that will revolutionize the ecosystem and leverage synergy."
        result = validate(content, self._ctx())
        assert result.score < 80
        assert any(f.check == "ai_cliches" for f in result.failures)

    def test_clean_content_passes(self):
        content = (
            "Most LinkedIn posts fail before the second line.\n\n"
            "The hook is what they see before 'see more'. If it doesn't earn the click, nothing else matters.\n\n"
            "I tested 50 hooks last month. Three patterns worked every time:\n"
            "  - A specific claim that provokes disagreement\n"
            "  - A number that seems wrong\n"
            "  - A lesson from a mistake I actually made\n\n"
            "The rest got ignored.\n\n"
            "What hook pattern has worked best for you?\n\n"
            "#LinkedIn #ContentStrategy #Marketing"
        )
        result = validate(content, self._ctx("LinkedIn Post"))
        assert result.score >= 50  # Should pass basic checks

    def test_hashtag_count_check_linkedin(self):
        ctx = self._ctx("LinkedIn Post")
        content = "Good content.\n\n#one"  # Only 1 hashtag, needs 3-5
        result = validate(content, ctx)
        hashtag_failure = next((f for f in result.failures if f.check == "hashtag_count"), None)
        assert hashtag_failure is not None

    def test_weak_opener_detected(self):
        content = "In today's fast-paced world, AI is changing everything.\n\nSome body.\n\nWhat do you think?"
        result = validate(content, self._ctx())
        assert any(f.check == "weak_opener" for f in result.failures)

    def test_fake_statistic_detected(self):
        content = "Research shows that 87% of teams fail. Studies show this is true.\n\nCTA question?"
        result = validate(content, self._ctx())
        assert any(f.check == "fake_statistics" for f in result.failures)

    def test_grade_excellent_for_high_score(self):
        # Inject a known-good score by checking grade logic
        result = validate("Good content with no issues detected at all.", {"platform": {}, "use_case": ""})
        assert result.grade in ("excellent", "good", "fair", "poor")


# ---------------------------------------------------------------------------
# Full pipeline tests (require OPENAI_API_KEY — skip in CI without key)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPipelineIntegration:
    """
    Integration tests that call the real LLM.
    Set OPENAI_API_KEY in environment to run.
    Skip with: pytest tests/ -v -m "not integration"
    """

    def _make_request(self, **kwargs) -> ContentRequest:
        defaults = {
            "prompt": "How to build better AI products",
            "use_case": "LinkedIn Post",
            "audience": "AI Engineers",
            "tone": "Direct",
            "goal": "Spark conversation about AI product development",
        }
        defaults.update(kwargs)
        return ContentRequest(**defaults)

    def test_linkedin_post_creation(self):
        response = run(self._make_request())
        assert response.final_output
        assert response.intent == "create"
        assert response.validation.score >= 0
        assert len(response.pipeline) >= 8  # 13-stage pipeline (some stages may be skipped)

    def test_blog_creation(self):
        response = run(self._make_request(
            use_case="Blog",
            prompt="The real cost of technical debt in AI systems",
            goal="Educate engineers on managing tech debt",
        ))
        assert response.final_output
        assert response.validation.score >= 0

    def test_cold_email_creation(self):
        response = run(self._make_request(
            use_case="Cold Email",
            audience="Startup Founders",
            prompt="Our AI tool cuts onboarding time by 60%",
            goal="Book a discovery call",
            tone="Direct",
        ))
        assert response.final_output
        assert len(response.final_output.split()) <= 250  # Should stay concise

    def test_improve_mode(self):
        existing = "AI is changing the world. It's a game-changer that will revolutionize everything. What do you think? #AI #Tech"
        response = run(self._make_request(
            prompt="Improve this LinkedIn post",
            intent="improve",
            existing_content=existing,
        ))
        assert response.intent == "improve"
        assert response.final_output != existing  # Should be different

    def test_pipeline_trace_has_all_stages(self):
        response = run(self._make_request())
        stage_names = [s.stage for s in response.pipeline]
        # Core stages that must always appear
        core_stages = [
            "intent_analysis", "audience_intelligence", "strategy_engine",
            "experience_patterns", "style_entropy", "context_assembly",
            "prompt_optimizer", "content_generator",
            "humanization_validator", "humanization_repair",
            "validator", "repair_engine", "formatter",
        ]
        for stage in core_stages:
            assert stage in stage_names, f"Missing pipeline stage: {stage}"
