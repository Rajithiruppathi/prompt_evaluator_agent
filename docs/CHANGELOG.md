# Changelog

All notable changes to this project are documented here.
Format: [Version] — Date — Summary, then Added / Modified / Removed / Fixed.

---

## [5.5.0] — 2026-05-27 — Persistent File Logging

Added a `FileHandler` alongside the existing `StreamHandler` in `app/main.py`.
All log output is now written to `logs/app.log` in append mode as well as the
console. The `logs/` directory is auto-created at startup if it does not exist.
Zero changes to business logic, configuration, or pipeline behaviour.

### Added
- `logs/app.log` — persistent log file; appended on every server start
- `Path("logs").mkdir(exist_ok=True)` in `app/main.py` — auto-creates the directory
- `logging.FileHandler("logs/app.log", mode="a")` alongside the existing
  `logging.StreamHandler()` in the `basicConfig` `handlers` list

### Modified
- `app/main.py` — `logging.basicConfig` replaced with explicit `handlers=[...]`;
  format and date strings extracted to module-level constants `_LOG_FORMAT`, `_LOG_DATE`;
  added `from pathlib import Path`

### Removed
- Nothing removed

---

## [5.4.0] — 2026-05-27 — Resilient Provider Chain

Added automatic retry and provider fallback to the LLM factory. Every LLM call
now goes through a `ResilientLLM` instance that tries providers in priority order:
primary → optional fallback → mock last resort. The pipeline never crashes from
an API failure. Structured logging covers every attempt: provider, latency, and
failure reason. All public interfaces preserved unchanged.

### Added
- `ResilientLLM` class in `app/core/llm.py` — wraps an ordered provider chain,
  retries each provider up to `LLM_RETRY_ATTEMPTS` times, falls through to next
  on exhaustion
- `_MockProvider` + `_MockFallbackResult` — no-op last-resort provider; always
  returns empty content instead of raising; guarantees `.invoke()` never throws
- `_ProviderEntry` NamedTuple — `(name: str, llm: Any)` — one entry per provider
  in the chain
- `_make_provider_llm(provider, model, temperature)` — instantiates a real
  `BaseChatModel` for the given provider (replaces old `_make_llm`)
- `_build_provider_chain(role, model, temperature)` — assembles the ordered
  `[primary?, fallback?, mock]` chain; skips any provider whose SDK is missing
- `FALLBACK_PROVIDER` constant in `config.py` — optional secondary provider
- `LLM_RETRY_ATTEMPTS` constant in `config.py` — attempts per provider before advancing
- `MODEL_DEFAULTS` (renamed from `_MODEL_DEFAULTS`) — now public so `llm.py` can
  look up fallback-provider model defaults
- `FALLBACK_PROVIDER=` and `LLM_RETRY_ATTEMPTS=1` entries in `.env.example`
- Structured log lines on every LLM call:
  - `LLM | role=X provider=Y attempt=A/B latency=Zms` (success)
  - `LLM | role=X provider=Y attempt=A/B FAILED: ErrorType: message` (failure)
  - `LLM | role=X provider=Y all N attempt(s) exhausted — trying next provider`
  - `LLM | role=X all real providers failed — returning empty mock response`

### Modified
- `app/core/llm.py` — rewritten internals; public API signature preserved
  - `get_llm(role)` now returns `ResilientLLM` (was `BaseChatModel`)
  - Named getters return `ResilientLLM` (was `BaseChatModel`)
  - `_pool` type changed from `dict[str, BaseChatModel]` to `dict[str, ResilientLLM]`
  - Old `_make_llm()` and `_get()` removed; replaced by `_make_provider_llm()` and
    `_build_provider_chain()`
- `app/core/config.py`:
  - `_MODEL_DEFAULTS` → `MODEL_DEFAULTS` (public rename)
  - Added `FALLBACK_PROVIDER`, `LLM_RETRY_ATTEMPTS`
- `.env.example` — `FALLBACK_PROVIDER` and `LLM_RETRY_ATTEMPTS` block added

### Removed
- `_make_llm()` (private — replaced by `_make_provider_llm()`)
- `_get()` (private — logic absorbed into `get_llm()`)

### Notes
- Fallback model names use the fallback provider's own `MODEL_DEFAULTS` — so if
  primary is OpenAI and fallback is Gemini, the fallback uses `gemini-2.5-pro` for
  the generator role, not `gpt-4o-mini`.
- When `FALLBACK_PROVIDER` is empty (default), the chain is `[primary, mock]` —
  one provider, no fallback, mock last resort.
- `_MockProvider` in the fallback chain is independent of `MOCK_MODE`. `MOCK_MODE`
  bypasses LLM calls at the application layer; `_MockProvider` is the infrastructure-
  layer safety net when all real providers fail at runtime.

---

## [5.3.0] — 2026-05-27 — Mock Mode for Local Development

Added `MOCK_MODE=true` support so the entire 13-stage pipeline can be exercised
without any API key or LLM provider configured. All deterministic stages run
normally. LLM calls in content generation and repair are replaced by a
deterministic fake response. Zero changes to the graph structure, routing logic,
or public API contract.

### Added
- `MOCK_MODE` boolean constant in `app/core/config.py` — reads `MOCK_MODE` env var
  (default: `false`)
- `_mock_generate()` helper in `app/agents/content_generator.py` — returns a
  deterministic practitioner-voiced fake response that includes the first line of
  the prompt for identification; exercises all downstream pipeline stages
- Mock branch in `generate()`: logs `[MOCK MODE ENABLED]`, returns `_mock_generate()`
  result, no LLM import triggered
- Mock branch in `repair_humanization()`: logs `[MOCK MODE ENABLED]`, skips only the
  LLM humanization pass; Phase 1 deterministic transition removal still runs
- Mock branch in `repair()`: logs `[MOCK MODE ENABLED]`, skips only the LLM surgical
  repair call; Step 1 deterministic repairs (hashtag count, length, exclamations) still run
- `MOCK_MODE=false` entry in `.env.example` with full explanation

### Modified
- `app/core/config.py` — added `MOCK_MODE` constant
- `app/agents/content_generator.py` — added `_mock_generate()` + `MOCK_MODE` branch
- `app/agents/repair_engine.py` — added `MOCK_MODE` guard in `repair()` and
  `repair_humanization()` LLM call sites; `MOCK_MODE` import added
- `.env.example` — `MOCK_MODE` block added at top with usage notes

### Removed
- Nothing removed

### Notes
- When `MOCK_MODE=true`, `generate()` never calls `generator_llm()`, so provider SDK
  imports (langchain_openai / langchain_google_genai) are never triggered. The pipeline
  runs with only `langchain_core` and deterministic stage code.
- Deterministic repair stages keep running in mock mode — this is intentional. They
  test real string-manipulation logic at zero API cost.
- The Phase 2 repair loop (`quality_repair → quality_validate`) will likely exhaust
  `MAX_REPAIR_ATTEMPTS` in mock mode since no LLM is improving the score.
  This is the expected behavior and exercises the convergence/max-attempts exit paths.
- No changes to `WorkflowState`, graph edges, routing functions, or `ContentResponse`.

---

## [5.2.0] — 2026-05-27 — Bounded Quality Repair Loop (Phase 2)

Implemented the iterative quality repair loop deferred in v5.0.0.
`quality_repair_node` now loops back to `quality_validate_node` after each repair attempt
instead of proceeding directly to `format`. The loop exits when quality is acceptable,
the repair budget is exhausted, or convergence is detected. `MAX_REPAIR_ATTEMPTS` (default 2)
is now fully enforced. Zero breaking changes to the public API or pipeline trace contract.

### Added
- `repair_attempt_count: int` field in `WorkflowState` — counts how many times
  `quality_repair_node` has executed in the current request
- `previous_quality_score: Optional[int]` field in `WorkflowState` — score before the
  most recent repair attempt; used for convergence comparison
- `convergence_reached: bool` field in `WorkflowState` — set to `True` by
  `quality_validate_node` when the new score is ≤ the previous score
- Loop exit logic in `route_quality()`: exits when score ≥ threshold, no failures remain,
  `repair_attempt_count >= MAX_REPAIR_ATTEMPTS`, or `convergence_reached`
- Convergence detection in `quality_validate_node`: compares current score to
  `previous_quality_score`; logs termination reason
- Per-iteration pipeline stage detail: re-validation passes now include
  `Re-validation N/MAX | delta=±D | [CONVERGED]` in the stage detail string
- Structured logging in `quality_repair_node`: logs attempt number, score before repair,
  failure count on each iteration
- Response `metadata` keys: `repair_attempt_count`, `convergence_reached`,
  `final_quality_score`

### Modified
- `app/workflows/state.py` — added 3 loop fields
- `app/workflows/nodes.py`:
  - `quality_validate_node` — convergence detection; skip record only on first pass
    (`repair_attempt_count == 0`); `convergence_reached` always returned in state dict
  - `quality_repair_node` — increments `repair_attempt_count`, stores
    `previous_quality_score`, updates both `working_content` AND `final` (so re-validation
    and format_node both see the repaired content); richer stage detail with attempt counter
- `app/workflows/graph.py`:
  - `route_quality()` — expanded with 4 exit conditions; imports `MAX_REPAIR_ATTEMPTS`
  - Edge changed: `quality_repair → format` replaced with `quality_repair → quality_validate`
- `app/workflows/content_workflow.py`:
  - Initial state: `repair_attempt_count=0`, `previous_quality_score=None`,
    `convergence_reached=False`
  - State unpack: reads `repair_attempt_count`, `convergence_reached`
  - `metadata`: adds `repair_attempt_count`, `convergence_reached`, `final_quality_score`

### Removed
- Nothing removed

### Notes
- Pipeline trace parity maintained: the `repair_engine: skipped` record is appended
  only on the first validate pass (`repair_attempt_count == 0`) — identical to v5.1.0
  behavior on the fast path. Subsequent re-validation passes do not append skip records.
- `format_node` unchanged — uses `state.get("final") or state["working_content"]`,
  which works for both the zero-repair and multi-repair paths.

---

## [5.1.0] — 2026-05-27 — Multi-Provider LLM Support

Added support for Google Gemini alongside OpenAI. Provider is selectable at
runtime via environment variable. Zero changes to any agent or workflow file.

### Added
- `LLM_PROVIDER` environment variable — selects `openai` or `gemini` at startup
- `GOOGLE_API_KEY` environment variable support
- `get_llm(role: str) → BaseChatModel` — central named factory in `app/core/llm.py`
- Gemini model defaults in `app/core/config.py`:
  - `gemini-2.5-flash` for intent and strategy roles
  - `gemini-2.5-pro` for generator and repair roles
- `langchain-google-genai>=2.0.0` in `requirements.txt`
- `_SUPPORTED_PROVIDERS` and `_ROLE_CONFIG` dicts in `llm.py` for validation and dispatch
- Invalid provider and invalid role `ValueError` with actionable messages

### Modified
- `app/core/llm.py`:
  - Top-level `from langchain_openai import ChatOpenAI` removed
  - All provider imports moved inside `_make_llm()` (lazy — only imported when active)
  - Return type of all four getters changed from `ChatOpenAI` to `BaseChatModel`
  - `_pool` type changed from `dict[str, ChatOpenAI]` to `dict[str, BaseChatModel]`
  - Four named getters now delegate to `get_llm(role)` instead of `_get()` directly
- `app/core/config.py`:
  - Added `LLM_PROVIDER` constant
  - Added `_MODEL_DEFAULTS` dict mapping each provider to role-specific model names
  - Four `*_MODEL` constants now derive default from `_MODEL_DEFAULTS[LLM_PROVIDER]`
- `requirements.txt` — added `langchain-google-genai>=2.0.0`
- `.env.example` — added `LLM_PROVIDER`, `GOOGLE_API_KEY`, documented both provider defaults

### Removed
- Nothing removed

---

## [5.0.0] — 2026-05-27 — LangGraph StateGraph Migration

Converted the monolithic sequential `run()` function into a compiled LangGraph
`StateGraph` with 13 nodes and 2 conditional repair branches. All agent files,
service files, schemas, and API routes are unchanged. Public interface preserved.

### Added
- `app/workflows/state.py` — `WorkflowState` TypedDict (`total=False`)
  - 9 input fields (mirrors `ContentRequest`)
  - ~20 intermediate fields (one per stage output)
  - `pipeline: list` for cumulative execution trace
- `app/workflows/nodes.py` — 13 node functions:
  `intent_node`, `audience_node`, `strategy_node`, `experience_node`,
  `entropy_node`, `context_node`, `generate_node`, `humanize_validate_node`,
  `humanize_repair_node`, `quality_validate_node`, `quality_repair_node`,
  `format_node`, `memory_node`
- `app/workflows/graph.py`:
  - `build_graph()` — assembles `StateGraph`, wires all edges, compiles
  - `route_humanization()` — conditional edge function (threshold: 60)
  - `route_quality()` — conditional edge function (threshold: 55 + failures)
  - `_graph` — module-level compiled graph singleton
- `docs/` directory (this directory) with `PROJECT_BRAIN.md`,
  `ARCHITECTURE_DECISIONS.md`, `CHANGELOG.md`, `ROADMAP.md`
- `LANGGRAPH_MIGRATION.md` — migration planning document (root level)

### Modified
- `app/workflows/content_workflow.py`:
  - Removed all 13 stage call sequences and local variable passing
  - `run()` now: builds `WorkflowState` from request → calls `_graph.invoke()` →
    assembles `ContentResponse` from final state
  - Module-level imports reduced to `ContentRequest`, `ContentResponse`,
    `HumanizationResult`, `WorkflowState`, `_graph`

### Removed
- Sequential pipeline body from `content_workflow.py` (all 13 stage calls)
- All intermediate local variable assignments that threaded state through the monolith

### Notes
- `ContentResponse` output is identical to v4.1.0 — same fields, same pipeline
  trace records, same stage names
- Pipeline trace parity: `humanize_validate_node` and `quality_validate_node` each
  append their respective "skipped" stage records when the repair branch is bypassed,
  preserving identical trace output on all execution paths

---

## [4.1.0] — Pre-2026-05-27 — Sequential Content Pipeline (Baseline)

> Captured from git commit f518779 "Updated AI Content Engine"

Production-grade sequential 13-stage content pipeline. All domain logic established
in this version; LangGraph migration in v5.0.0 preserves all functionality.

### System at this version
- FastAPI application with 6 endpoints
- Single `run()` function in `content_workflow.py` orchestrating 13 stages
- 8 agent files in `app/agents/`
- 4 service files in `app/services/`
- 7 context files in `app/context/`
- Full knowledge base: 8 platforms, 7 audiences, 7 styles
- 13-check deterministic quality validator
- 4-dimension humanization validator
- Conditional humanization repair (deterministic + LLM)
- Conditional quality repair (deterministic + LLM)
- Platform-native formatter
- In-process content memory (ring buffer, 50 entries)
- Per-(use_case, audience) failure memory
- Provider: OpenAI only, hardwired via `from langchain_openai import ChatOpenAI`
- Model: `gpt-4o-mini` across all four roles

---

## [1.0.0] — Initial — Fresh Clean Version

> Captured from git commit 877b6f5 "Fresh clean version"

Initial project scaffold.
