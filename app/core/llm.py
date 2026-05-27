"""
LLM factory — one instance per role, shared across the pipeline.

Provider is selected via LLM_PROVIDER in config (openai | gemini).
No module should instantiate a chat model directly; use the public getters
or get_llm(role) instead.

Public API (unchanged from before):
    intent_llm()    → BaseChatModel
    strategy_llm()  → BaseChatModel
    generator_llm() → BaseChatModel
    repair_llm()    → BaseChatModel

Internal central factory:
    get_llm(role)   → BaseChatModel   role ∈ {"intent", "strategy", "generator", "repair"}
"""

from langchain_core.language_models import BaseChatModel

from app.core.config import (
    LLM_PROVIDER,
    INTENT_MODEL,    INTENT_TEMPERATURE,
    STRATEGY_MODEL,  STRATEGY_TEMPERATURE,
    GENERATE_MODEL,  GENERATE_TEMPERATURE,
    REPAIR_MODEL,    REPAIR_TEMPERATURE,
)

_SUPPORTED_PROVIDERS = {"openai", "gemini"}

_pool: dict[str, BaseChatModel] = {}


def _make_llm(model: str, temperature: float) -> BaseChatModel:
    """Instantiate the correct chat model for the configured provider."""
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI  # type: ignore[import-untyped]
        return ChatOpenAI(model=model, temperature=temperature)  # type: ignore[call-arg]

    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import-untyped]
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)

    raise ValueError(
        f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. "
        f"Valid options: {sorted(_SUPPORTED_PROVIDERS)}"
    )


def _get(key: str, model: str, temperature: float) -> BaseChatModel:
    if key not in _pool:
        _pool[key] = _make_llm(model, temperature)
    return _pool[key]


# ---------------------------------------------------------------------------
# Central factory — use this when adding new callers
# ---------------------------------------------------------------------------

_ROLE_CONFIG: dict[str, tuple[str, float]] = {
    "intent":    (INTENT_MODEL,   INTENT_TEMPERATURE),
    "strategy":  (STRATEGY_MODEL, STRATEGY_TEMPERATURE),
    "generator": (GENERATE_MODEL, GENERATE_TEMPERATURE),
    "repair":    (REPAIR_MODEL,   REPAIR_TEMPERATURE),
}


def get_llm(role: str) -> BaseChatModel:
    """Return the shared LLM instance for a named pipeline role."""
    if role not in _ROLE_CONFIG:
        raise ValueError(
            f"Unknown LLM role: {role!r}. Valid roles: {sorted(_ROLE_CONFIG)}"
        )
    model, temperature = _ROLE_CONFIG[role]
    return _get(role, model, temperature)


# ---------------------------------------------------------------------------
# Named getters — preserved for all existing callers
# ---------------------------------------------------------------------------

def intent_llm()    -> BaseChatModel: return get_llm("intent")
def strategy_llm()  -> BaseChatModel: return get_llm("strategy")
def generator_llm() -> BaseChatModel: return get_llm("generator")
def repair_llm()    -> BaseChatModel: return get_llm("repair")
