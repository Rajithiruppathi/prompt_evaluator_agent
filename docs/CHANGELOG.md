# Changelog

All notable changes to this project are documented here.
Format: [Version] — Date — Summary, then Added / Modified / Removed / Fixed.

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
