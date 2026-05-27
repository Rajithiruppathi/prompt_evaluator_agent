# PROJECT BRAIN — Prompt Evaluator Agent

> **Source of truth for the current state of the system.**
> Updated after every architectural change. Never let this drift from the code.

---

## System Overview

A production-grade AI content generation pipeline that accepts a topic or brief and
produces platform-optimized, audience-aware, humanized content across 8 supported
formats. The pipeline is executed as a compiled LangGraph `StateGraph` with 13 nodes
and 2 conditional repair branches.

**Current Version:** 5.1.0
**Stack:** FastAPI · LangGraph · LangChain · OpenAI or Gemini (provider-selectable)

---

## Current Architecture

```
HTTP Client
    │
    ▼
FastAPI  (app/main.py + app/api/routes.py)
    │
    │  POST /generate
    ▼
content_workflow.run(ContentRequest)
    │
    │  builds WorkflowState, calls _graph.invoke()
    ▼
LangGraph StateGraph  (app/workflows/graph.py)
    │
    ├─ [intent]             Stage 1  — deterministic intent detection
    ├─ [audience]           Stage 2  — audience profile loader
    ├─ [strategy]           Stage 3  — platform + style strategy
    ├─ [experience]         Stage 3b — domain-relevant experience patterns
    ├─ [entropy]            Stage 3c — per-request style variation + anti-repetition
    ├─ [context]            Stage 3d+4 — ContextPackage assembly + prompt serialization
    ├─ [generate]           Stage 5  — LLM call (provider-selectable)
    ├─ [humanize_validate]  Stage 5b — 4-dimension humanization scoring
    ├─ ── score < 60 ──► [humanize_repair]  Stage 5c (conditional)
    ├─ [quality_validate]   Stage 6  — 13-check deterministic quality scoring
    ├─ ── score < 55 ──► [quality_repair]   Stage 7 (conditional)
    ├─ [format]             Stage 8  — platform-native formatting
    └─ [memory]             Stage 8b — content memory + failure recording
    │
    ▼
ContentResponse  (assembled in content_workflow.py)
    │
    ▼
HTTP Client
```

---

## LangGraph Graph Structure

### Nodes (13 total)

| Node Name | Stage | Function Called | LLM? |
|---|---|---|---|
| `intent` | 1 | `analyze_intent()` | No |
| `audience` | 2 | `build_audience_context()` | No |
| `strategy` | 3 | `build_strategy()` | No |
| `experience` | 3b | `select_patterns()` | No |
| `entropy` | 3c | `get_entropy_directives()` + `content_memory` | No |
| `context` | 3d+4 | `build_generation_prompt_with_context()` | No |
| `generate` | 5 | `generate()` | **Yes** |
| `humanize_validate` | 5b | `validate_humanization()` | No |
| `humanize_repair` | 5c | `repair_humanization()` | **Yes** (conditional) |
| `quality_validate` | 6 | `validate()` | No |
| `quality_repair` | 7 | `repair()` | **Yes** (conditional) |
| `format` | 8 | `format_output()` | No |
| `memory` | 8b | `content_memory.register()` + `failure_memory.record()` | No |

### Edges

| From | To | Type | Condition |
|---|---|---|---|
| `intent` | `audience` | Normal | — |
| `audience` | `strategy` | Normal | — |
| `strategy` | `experience` | Normal | — |
| `experience` | `entropy` | Normal | — |
| `entropy` | `context` | Normal | — |
| `context` | `generate` | Normal | — |
| `generate` | `humanize_validate` | Normal | — |
| `humanize_validate` | `humanize_repair` | **Conditional** | score < 60 |
| `humanize_validate` | `quality_validate` | **Conditional** | score ≥ 60 |
| `humanize_repair` | `quality_validate` | Normal | — |
| `quality_validate` | `quality_repair` | **Conditional** | score < 55 AND failures exist |
| `quality_validate` | `format` | **Conditional** | score ≥ 55 OR no failures |
| `quality_repair` | `format` | Normal | — |
| `format` | `memory` | Normal | — |
| `memory` | END | Normal | — |

### Execution Paths

- **Fast path** (both repairs skipped): 11 nodes execute
- **Humanization repair only**: 12 nodes
- **Quality repair only**: 12 nodes
- **Both repairs**: 13 nodes (all nodes)

---

## WorkflowState

Defined in `app/workflows/state.py`. TypedDict with `total=False` — keys are added
progressively as each node executes.

```
Inputs:        prompt, use_case, audience, goal, tone, style,
               intent_input, existing_content, target_use_case

Stage outputs: intent → audience_context → strategy →
               experience_patterns, experience_block →
               entropy_directives, entropy_block, memory_directive →
               optimized_prompt, context_package, pre_check →
               draft, working_content →
               humanization_result, humanization_repaired →
               validation →
               quality_repaired, final →
               pipeline (cumulative list of PipelineStage records)
```

Non-serialisable objects (`context_package`, `humanization_result`, `validation`) are
typed as `Any` — they are live in-process objects, never persisted or checkpointed.

---

## LLM Factory

**File:** `app/core/llm.py`

Provider-agnostic factory. Supports two providers selectable via `LLM_PROVIDER` env var.
Four named roles; each is a lazy-instantiated singleton in `_pool`.

| Role | Getter | Default — OpenAI | Default — Gemini | Temp |
|---|---|---|---|---|
| intent | `intent_llm()` | gpt-4o-mini | gemini-2.5-flash | 0.0 |
| strategy | `strategy_llm()` | gpt-4o-mini | gemini-2.5-flash | 0.2 |
| generator | `generator_llm()` | gpt-4o-mini | gemini-2.5-pro | 0.7 |
| repair | `repair_llm()` | gpt-4o-mini | gemini-2.5-pro | 0.3 |

`intent_llm()` and `strategy_llm()` are defined but currently have no callers —
`intent_node` and `strategy_node` are fully deterministic.

Central factory: `get_llm(role: str) → BaseChatModel`

---

## API Contracts

**Base URL:** `http://localhost:8000`

| Method | Path | Handler | Description |
|---|---|---|---|
| POST | `/generate` | `routes.generate` | Full 13-stage pipeline |
| POST | `/validate` | `routes.validate_content` | Standalone content validation |
| GET | `/styles` | `routes.get_styles` | List 7 writing styles |
| GET | `/platforms` | `routes.get_platforms` | List 8 platforms |
| GET | `/audiences` | `routes.get_audiences` | List 7 audience profiles |
| GET | `/use-cases` | `routes.get_use_cases` | Alias for /platforms |
| GET | `/health` | *(not in routes.py)* | Health check |

### ContentRequest schema
```
prompt           str       required   Topic or content brief
use_case         str       required   Target platform
audience         str       required   Target audience
goal             str       required   Content objective
tone             str       "Professional"
style            str|None  None       Writing style identity
intent           str|None  None       Auto-detected if omitted
existing_content str|None  None       For improve/rewrite/convert
target_use_case  str|None  None       For convert intent
```

### ContentResponse schema
```
intent, use_case, audience, audience_profile, style, tone
optimized_prompt, draft_output, final_output
validation       ValidationResult
humanization     HumanizationResult
repaired         bool
pipeline         list[PipelineStage]
metadata         dict
```

---

## Quality Framework

### Quality Validation (Stage 6) — 13 deterministic checks

`ai_cliche` · `generic_phrases` · `weak_opener` · `fake_statistics` ·
`sentence_length` · `repetition` · `exclamations` · `cta_quality` ·
`hashtag_count` · `content_length` · `title_presence` · `paragraph_length` ·
`passive_voice`

Score 0–100. Severity weights: critical=15, high=10, medium=5, low=2.

### Humanization Validation (Stage 5b) — 4 dimensions (0–25 each)

| Dimension | What it measures |
|---|---|
| Specificity | Concrete numbers, tool names, timeframes |
| Tension | Conflict, failure, narrative reversal |
| Originality | Absence of clichés and robotic transitions |
| Experience | Practitioner-derived signals |

### Thresholds

| Variable | Default | Effect |
|---|---|---|
| `VALIDATION_PASS_THRESHOLD` | 75 | Score ≥ 75 → approved as-is |
| `AUTO_REPAIR_THRESHOLD` | 55 | Score < 55 AND failures → quality repair |
| `HUMANIZATION_REPAIR_THRESHOLD` | 60 | Score < 60 → humanization repair |
| `MAX_REPAIR_ATTEMPTS` | 2 | Configured but not yet enforced as a loop |

---

## Memory Systems

Two in-process singleton stores (not persisted across restarts):

| Module | Type | What it tracks |
|---|---|---|
| `app/services/content_memory.py` | Ring buffer (50 entries) | Hook patterns, transitions, CTAs — provides variety directives |
| `app/context/failure_memory.py` | Per-(use_case, audience) dict | Validator failures, humanization issues, banned phrases — fed back into future prompts |

Both are thread-safe via `Lock`. Neither survives process restart. No Redis/DB backing.

---

## Supported Platforms (8)

`LinkedIn Post` · `Blog` · `Cold Email` · `Ad Copy` · `Twitter Thread` ·
`SEO Article` · `Technical Post` · `Educational Content`

## Supported Audiences (7)

`AI Engineers` · `Developers` · `Startup Founders` · `Marketers` ·
`Students` · `Enterprise Buyers` · `SEO Experts`

## Supported Writing Styles (7)

`Technical Educator` · `Contrarian Expert` · `Founder Storyteller` ·
`Minimalist Operator` · `Strategic Advisor` · `Storyteller` · `Analyst`

## Intent Modes (4)

`create` · `improve` · `rewrite` · `convert`

---

## Current Capabilities

- Generates platform-native content across 8 formats
- Audience-aware vocabulary, trust signals, pain points
- 4 intent modes with auto-detection
- Per-request style entropy to prevent AI template rhythm
- 54 banned AI transition phrases
- 25+ domain-specific experience patterns (production incidents, tradeoffs, failures)
- Deterministic 13-check quality scoring (no LLM required)
- 4-dimension humanization scoring (no LLM required)
- Conditional repair for both quality and humanization
- Platform-native formatting (hashtag positioning, tweet numbering, etc.)
- Content memory (ring buffer, anti-repetition)
- Failure memory (per use-case+audience, feeds future prompts)
- Full pipeline execution trace in every response
- Provider-selectable LLM backend (OpenAI or Gemini)
- LangGraph StateGraph orchestration with conditional branches

## Current Limitations

- Memory stores are in-process only — do not survive restart, not safe for multi-instance deployment
- No re-validation after quality repair — repair may introduce new issues
- `intent_llm()` and `strategy_llm()` have no callers — intent and strategy are deterministic only
- Pre-generation check (`pre_check`) stored in state but no node acts on failures
- `MAX_REPAIR_ATTEMPTS` is configured but not wired as a graph loop — repair runs at most once
- No checkpointing — graph state cannot be resumed or inspected mid-run
- No human-in-the-loop interruption point
- `experience_node` and `entropy_node` are independent but run serially

---

## Folder Structure

```
prompt_evaluator_agent/
│
├── main.py                         # Entry point — delegates to app/main.py
├── requirements.txt                # All dependencies
├── .env.example                    # Documented environment variable template
├── README.md                       # User-facing quickstart
├── LANGGRAPH_MIGRATION.md          # Original migration planning document
│
├── docs/                           # Technical documentation (this directory)
│   ├── PROJECT_BRAIN.md            # ← YOU ARE HERE — current system state
│   ├── ARCHITECTURE_DECISIONS.md   # Design decisions and tradeoffs
│   ├── CHANGELOG.md                # Versioned change history
│   └── ROADMAP.md                  # Planned enhancements
│
├── app/
│   ├── main.py                     # FastAPI app definition
│   │
│   ├── api/
│   │   └── routes.py               # All API endpoints
│   │
│   ├── workflows/                  # LangGraph orchestration layer
│   │   ├── __init__.py
│   │   ├── state.py                # WorkflowState TypedDict
│   │   ├── nodes.py                # 13 node functions (one per pipeline stage)
│   │   ├── graph.py                # StateGraph builder + compiled singleton
│   │   └── content_workflow.py     # run() — entry point for routes
│   │
│   ├── agents/                     # Pipeline stage executors (unchanged by LangGraph)
│   │   ├── intent_analyzer.py      # Stage 1 — deterministic intent detection
│   │   ├── audience_engine.py      # Stage 2 — audience profile loader
│   │   ├── strategy_engine.py      # Stage 3 — platform + style strategy
│   │   ├── prompt_optimizer.py     # Stage 3d — context-engine prompt builder
│   │   ├── content_generator.py    # Stage 5 — LLM call
│   │   ├── validator.py            # Stage 6 — 13-check quality scorer
│   │   ├── repair_engine.py        # Stages 5c + 7 — deterministic + LLM repair
│   │   └── formatter.py            # Stage 8 — platform-native formatting
│   │
│   ├── context/                    # Context Engineering package
│   │   ├── __init__.py             # Exports validate_banned()
│   │   ├── context_builder.py      # ContextPackage dataclass + to_prompt()
│   │   ├── platform_context.py     # Typed platform rule objects
│   │   ├── audience_context.py     # Typed audience profile objects
│   │   ├── style_context.py        # Typed style behavior objects
│   │   ├── examples_context.py     # Few-shot good/bad example objects
│   │   ├── failure_memory.py       # Per-(use_case, audience) failure tracker
│   │   └── banned_phrases.py       # Centralized banned phrase registry
│   │
│   ├── services/                   # Humanization + entropy services
│   │   ├── experience_patterns.py  # 25+ production incident/tradeoff patterns
│   │   ├── style_entropy.py        # Per-request variation directives + banned transitions
│   │   ├── human_validator.py      # 4-dimension humanization scorer
│   │   └── content_memory.py       # Ring-buffer anti-repetition tracker
│   │
│   ├── knowledge/                  # Static knowledge base
│   │   ├── platforms/profiles.py   # 8 platform definitions
│   │   ├── audiences/profiles.py   # 7 audience profiles
│   │   ├── styles/profiles.py      # 7 writing style identities
│   │   └── examples/
│   │       └── content_examples.py # Few-shot learning examples
│   │
│   ├── schemas/
│   │   ├── request.py              # ContentRequest, ValidateRequest
│   │   └── response.py             # ContentResponse, ValidationResult, HumanizationResult, PipelineStage
│   │
│   └── core/
│       ├── config.py               # Env config, thresholds, per-provider model defaults
│       ├── llm.py                  # Provider-agnostic LLM factory (OpenAI + Gemini)
│       └── prompts.py              # Prompt assembly utilities
│
└── tests/
    └── test_workflow.py            # Unit + integration tests
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openai` | Provider: `openai` or `gemini` |
| `OPENAI_API_KEY` | *(required if openai)* | OpenAI API key |
| `GOOGLE_API_KEY` | *(required if gemini)* | Google AI API key |
| `INTENT_MODEL` | provider default | Model for intent detection |
| `STRATEGY_MODEL` | provider default | Model for strategy |
| `GENERATE_MODEL` | provider default | Model for content generation |
| `REPAIR_MODEL` | provider default | Model for repair |
| `INTENT_TEMPERATURE` | `0.0` | |
| `STRATEGY_TEMPERATURE` | `0.2` | |
| `GENERATE_TEMPERATURE` | `0.7` | |
| `REPAIR_TEMPERATURE` | `0.3` | |
| `VALIDATION_PASS_THRESHOLD` | `75` | Quality score: skip repair |
| `AUTO_REPAIR_THRESHOLD` | `55` | Quality score: trigger repair |
| `HUMANIZATION_REPAIR_THRESHOLD` | `60` | Humanization score: trigger repair |
| `MAX_REPAIR_ATTEMPTS` | `2` | Max repair cycles (not yet looped) |

---

*Last updated: 2026-05-27 — v5.1.0*
