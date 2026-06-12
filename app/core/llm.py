"""
LLM factory — resilient provider chain with automatic retry and fallback.

Provider priority (per request):
    1. LLM_PROVIDER     (primary, from env — openai or gemini)
    2. FALLBACK_PROVIDER (secondary, from env — optional)
    3. _MockProvider     (last resort — always succeeds, returns empty content)

Each real provider is tried LLM_RETRY_ATTEMPTS times before the chain advances.
The mock provider guarantees .invoke() never raises, so the pipeline never
crashes from an LLM failure.

Public API (unchanged):
    intent_llm()    → ResilientLLM
    strategy_llm()  → ResilientLLM
    generator_llm() → ResilientLLM
    repair_llm()    → ResilientLLM
    get_llm(role)   → ResilientLLM   role ∈ {"intent", "strategy", "generator", "repair"}

All returned objects expose .invoke() with the same call signature as BaseChatModel.
"""

import time
import logging
from typing import Any, NamedTuple

from langchain_core.language_models import BaseChatModel

from app.core.config import (
    LLM_PROVIDER,
    FALLBACK_PROVIDER,
    LLM_RETRY_ATTEMPTS,
    MODEL_DEFAULTS,
    INTENT_MODEL,    INTENT_TEMPERATURE,
    STRATEGY_MODEL,  STRATEGY_TEMPERATURE,
    GENERATE_MODEL,  GENERATE_TEMPERATURE,
    REPAIR_MODEL,    REPAIR_TEMPERATURE,
)

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS = {"openai", "gemini"}


# ---------------------------------------------------------------------------
# Mock last-resort provider — always succeeds, never calls any API
# ---------------------------------------------------------------------------

class _MockFallbackResult:
    """Minimal response object (AIMessage-compatible). Returned when all real providers fail."""
    def __init__(self) -> None:
        self.content: str = ""


class _MockProvider:
    """No-op provider. Returns empty content. Used only when every real provider has failed."""
    def invoke(self, prompt: Any, **kwargs: Any) -> _MockFallbackResult:
        return _MockFallbackResult()


# ---------------------------------------------------------------------------
# Provider chain entry
# ---------------------------------------------------------------------------

class _ProviderEntry(NamedTuple):
    name: str
    llm: Any  # BaseChatModel | _MockProvider


# ---------------------------------------------------------------------------
# ResilientLLM — ordered provider chain with retry + fallback
# ---------------------------------------------------------------------------

class ResilientLLM:
    """
    Wraps an ordered list of providers. On .invoke():

      For each provider in [primary, fallback?, mock]:
        Retry up to LLM_RETRY_ATTEMPTS times.
        On success → return result immediately.
        On exhaustion → advance to next provider.

    The mock provider is always last and never raises, so the pipeline
    continues even when every configured API is unavailable.
    """

    def __init__(self, role: str, chain: list[_ProviderEntry]) -> None:
        self._role = role
        self._chain = chain

    def invoke(self, prompt: Any, **kwargs: Any) -> Any:
        last_error: Exception | None = None

        for entry in self._chain:
            if isinstance(entry.llm, _MockProvider):
                logger.error(
                    f"LLM | role={self._role} all real providers failed — "
                    f"returning empty mock response. Check API keys and provider config."
                )

            for attempt in range(1, LLM_RETRY_ATTEMPTS + 1):
                try:
                    t0 = time.perf_counter()
                    result = entry.llm.invoke(prompt, **kwargs)
                    latency_ms = (time.perf_counter() - t0) * 1000

                    if not isinstance(entry.llm, _MockProvider):
                        logger.info(
                            f"LLM | role={self._role} provider={entry.name} "
                            f"attempt={attempt}/{LLM_RETRY_ATTEMPTS} "
                            f"latency={latency_ms:.0f}ms"
                        )
                    return result

                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        f"LLM | role={self._role} provider={entry.name} "
                        f"attempt={attempt}/{LLM_RETRY_ATTEMPTS} FAILED: "
                        f"{type(exc).__name__}: {exc}"
                    )

            logger.warning(
                f"LLM | role={self._role} provider={entry.name} "
                f"all {LLM_RETRY_ATTEMPTS} attempt(s) exhausted — trying next provider"
            )

        # Unreachable: _MockProvider.invoke() never raises.
        raise RuntimeError(
            f"All LLM providers failed for role={self._role!r}"
        ) from last_error


# ---------------------------------------------------------------------------
# Provider instantiation
# ---------------------------------------------------------------------------

def _make_provider_llm(provider: str, model: str, temperature: float) -> BaseChatModel:
    """Instantiate a real chat model for the given provider. May raise on missing SDK."""
    if provider == "openai":
        from langchain_openai import ChatOpenAI  # type: ignore[import-untyped]
        return ChatOpenAI(model=model, temperature=temperature)  # type: ignore[call-arg]

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import-untyped]
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)

    raise ValueError(
        f"Unsupported provider={provider!r}. Valid options: {sorted(_SUPPORTED_PROVIDERS)}"
    )


def _build_provider_chain(role: str, model: str, temperature: float) -> list[_ProviderEntry]:
    """
    Construct the ordered provider chain for a given role.

    Slots:
      1. Primary   — LLM_PROVIDER (always attempted)
      2. Fallback  — FALLBACK_PROVIDER (if set, different from primary, and valid)
      3. Mock      — always appended as last resort
    """
    chain: list[_ProviderEntry] = []

    # 1. Primary provider
    try:
        primary = _make_provider_llm(LLM_PROVIDER, model, temperature)
        chain.append(_ProviderEntry(name=LLM_PROVIDER, llm=primary))
        logger.debug(f"LLM chain | role={role} primary={LLM_PROVIDER} model={model}")
    except Exception as exc:
        logger.warning(
            f"LLM chain | role={role} primary={LLM_PROVIDER} "
            f"unavailable at startup — {type(exc).__name__}: {exc}"
        )

    # 2. Fallback provider (only if configured, valid, and different from primary)
    is_valid_fallback = (
        bool(FALLBACK_PROVIDER)
        and FALLBACK_PROVIDER in _SUPPORTED_PROVIDERS
        and FALLBACK_PROVIDER != LLM_PROVIDER
    )
    if is_valid_fallback:
        # Use the fallback provider's own model defaults for the role
        fallback_model = MODEL_DEFAULTS.get(FALLBACK_PROVIDER, {}).get(role, model)
        try:
            fallback = _make_provider_llm(FALLBACK_PROVIDER, fallback_model, temperature)
            chain.append(_ProviderEntry(name=FALLBACK_PROVIDER, llm=fallback))
            logger.debug(
                f"LLM chain | role={role} fallback={FALLBACK_PROVIDER} "
                f"model={fallback_model}"
            )
        except Exception as exc:
            logger.warning(
                f"LLM chain | role={role} fallback={FALLBACK_PROVIDER} "
                f"unavailable at startup — {type(exc).__name__}: {exc}"
            )

    # 3. Mock — always last, guarantees .invoke() never raises
    chain.append(_ProviderEntry(name="mock", llm=_MockProvider()))

    provider_names = [e.name for e in chain]
    logger.debug(f"LLM chain | role={role} chain={provider_names}")
    return chain


# ---------------------------------------------------------------------------
# Pool — one ResilientLLM per role, lazily initialized
# ---------------------------------------------------------------------------

_ROLE_CONFIG: dict[str, tuple[str, float]] = {
    "intent":    (INTENT_MODEL,   INTENT_TEMPERATURE),
    "strategy":  (STRATEGY_MODEL, STRATEGY_TEMPERATURE),
    "generator": (GENERATE_MODEL, GENERATE_TEMPERATURE),
    "repair":    (REPAIR_MODEL,   REPAIR_TEMPERATURE),
}

_pool: dict[str, ResilientLLM] = {}


# ---------------------------------------------------------------------------
# Central factory — use this when adding new callers
# ---------------------------------------------------------------------------

def get_llm(role: str) -> ResilientLLM:
    """Return (or create) the resilient LLM chain for a named pipeline role."""
    if role not in _ROLE_CONFIG:
        raise ValueError(
            f"Unknown LLM role: {role!r}. Valid roles: {sorted(_ROLE_CONFIG)}"
        )
    if role not in _pool:
        model, temperature = _ROLE_CONFIG[role]
        _pool[role] = ResilientLLM(
            role=role,
            chain=_build_provider_chain(role, model, temperature),
        )
    return _pool[role]


# ---------------------------------------------------------------------------
# Named getters — preserved for all existing callers
# ---------------------------------------------------------------------------

def intent_llm()    -> ResilientLLM: return get_llm("intent")
def strategy_llm()  -> ResilientLLM: return get_llm("strategy")
def generator_llm() -> ResilientLLM: return get_llm("generator")
def repair_llm()    -> ResilientLLM: return get_llm("repair")
