# Roadmap

> Planned enhancements, in-progress work, and future milestones.
> Mark items complete when shipped and record the version in CHANGELOG.md.

---

## ✅ Completed

### v5.0.0 — LangGraph StateGraph Migration
- [x] Convert monolithic `run()` to compiled `StateGraph`
- [x] Define `WorkflowState` TypedDict
- [x] Create 13 graph nodes (one per pipeline stage)
- [x] Wire 2 conditional repair branches as graph edges
- [x] Preserve public `run(ContentRequest) → ContentResponse` signature
- [x] Preserve pipeline trace parity (skipped stage records on bypass paths)

### v5.1.0 — Multi-Provider LLM Support
- [x] Provider-agnostic `get_llm(role)` factory
- [x] OpenAI support (existing, preserved)
- [x] Google Gemini support (`langchain-google-genai`)
- [x] `LLM_PROVIDER` env var for runtime provider selection
- [x] Per-provider model name defaults in `config.py`
- [x] Lazy provider imports (only active SDK loaded)

### v5.2.0 — Bounded Quality Repair Loop (Phase 2)
- [x] Add `repair_attempt_count`, `previous_quality_score`, `convergence_reached` to `WorkflowState`
- [x] Loop `quality_repair → quality_validate` (replaced `quality_repair → format` edge)
- [x] Expanded `route_quality()`: 4 exit conditions (score, no failures, max attempts, convergence)
- [x] Convergence detection in `quality_validate_node` (score ≤ previous → stop)
- [x] Per-iteration stage detail with attempt counter and score delta
- [x] Structured repair loop logging (attempt number, score before, termination reason)
- [x] `repair_attempt_count`, `convergence_reached`, `final_quality_score` in response metadata
- [x] `MAX_REPAIR_ATTEMPTS` now fully enforced

### v5.3.0 — Mock Mode for Local Development
- [x] `MOCK_MODE` env var in `config.py`
- [x] `_mock_generate()` deterministic fake response in `content_generator.py`
- [x] Mock branch in `repair_humanization()` — skips LLM, keeps deterministic pass
- [x] Mock branch in `repair()` — skips LLM, keeps deterministic pass
- [x] `[MOCK MODE ENABLED]` log on every bypassed LLM call
- [x] `.env.example` updated with `MOCK_MODE=false` and usage notes
- [x] README testing instructions for running without API keys

### v5.4.0 — Resilient Provider Chain
- [x] `ResilientLLM` class with ordered provider chain (primary → fallback → mock)
- [x] Per-provider retry loop (`LLM_RETRY_ATTEMPTS`)
- [x] `_MockProvider` last-resort — pipeline never crashes on API failure
- [x] `FALLBACK_PROVIDER` env var — optional secondary provider
- [x] `LLM_RETRY_ATTEMPTS` env var — configurable retry count
- [x] Structured log lines: provider, attempt, latency, failure reason
- [x] `MODEL_DEFAULTS` renamed public for cross-module access

### v5.5.0 — Persistent File Logging
- [x] `logs/app.log` written in append mode alongside existing console output
- [x] `logs/` directory auto-created at startup via `Path("logs").mkdir(exist_ok=True)`
- [x] Explicit `handlers=[StreamHandler, FileHandler]` in `basicConfig`

---

## 🔄 In Progress

*Nothing currently in progress.*

---

## 📋 Planned — Near Term

---

### v5.6.0 — Persistent Memory Backend
**Priority:** High
**Why:** `content_memory` and `failure_memory` are in-process singletons — they
do not survive restarts and are not safe for multi-instance deployments.

- [ ] Define a `MemoryBackend` Protocol with `register()`, `get_variety_directive()`,
      `record_failure()`, `get_failures()` methods
- [ ] Implement `InProcessMemoryBackend` (current behavior, default)
- [ ] Implement `RedisMemoryBackend` (production path)
- [ ] Wire backend selection via `MEMORY_BACKEND=memory|redis` env var
- [ ] Add `REDIS_URL` env var support
- [ ] Update `content_memory.py` and `failure_memory.py` to delegate to backend
- [ ] Update `PROJECT_BRAIN.md` limitations section

**Estimated scope:** 4–6 files

---

### v5.7.0 — LangGraph Checkpointing
**Priority:** Medium
**Why:** Enables resume-from-checkpoint for failed runs, per-request state inspection,
and is a prerequisite for human-in-the-loop interruption.

- [ ] Define a custom serialiser for `context_package`, `humanization_result`,
      `validation` (currently `Any` — not JSON-serialisable)
- [ ] Wire `MemorySaver` or `SqliteSaver` checkpointer into `build_graph()`
- [ ] Add `thread_id` to request or derive from `use_case + audience + timestamp`
- [ ] Expose checkpoint state via a new `GET /run/{thread_id}` endpoint

**Blocker:** `context_package` uses live Python objects — needs a serialisation
strategy before checkpointing is viable.

---

### v5.8.0 — Parallel Stage Execution
**Priority:** Low
**Why:** `experience_node` and `entropy_node` are currently sequential but are
fully independent — both only require inputs already available after `strategy_node`.
Running them in parallel would reduce latency on the pipeline backbone.

- [ ] Verify `experience_node` and `entropy_node` have no shared mutable state
- [ ] Change graph edges: `strategy → {experience, entropy}` (fan-out)
      then `{experience, entropy} → context` (fan-in via a join node or direct)
- [ ] Profile actual latency improvement (both stages are lightweight — verify
      the overhead of parallelism doesn't exceed the gain)

**Note:** LangGraph supports fan-out natively — both nodes can be added as targets
of the same source edge. State merging handles fan-in automatically.

---

## 📋 Planned — Medium Term

### v6.0.0 — Human-in-the-Loop Quality Review
**Priority:** Medium
**Why:** When quality score is borderline (55–75), a human reviewer should be able
to approve, reject, or provide feedback before the response is returned.

- [ ] Add `__interrupt__` after `quality_validate_node` when score is in (55, 75)
- [ ] Expose a `POST /run/{thread_id}/resume` endpoint accepting reviewer feedback
- [ ] Feed reviewer feedback into `context_package` feedback field for re-generation
- [ ] Update response schema with `requires_review: bool` and `thread_id`

**Prerequisite:** v5.7.0 (checkpointing) must be complete first.

---

### v6.1.0 — LLM-Assisted Intent and Strategy
**Priority:** Low
**Why:** `intent_llm()` and `strategy_llm()` are defined but never called.
For ambiguous inputs, the current deterministic signal-word matching may misclassify.

- [ ] Add LLM fallback in `intent_analyzer.py` when no signal words match and no
      `existing_content` — call `intent_llm()` with a few-shot prompt
- [ ] Add LLM-assisted platform selection in `strategy_engine.py` when `use_case`
      does not exactly match a known profile
- [ ] Add confidence score to intent result

---

### v6.2.0 — Pre-Generation Check Gate
**Priority:** Low
**Why:** `pre_check` is stored in `WorkflowState` by `context_node` but no node
reads it. If `pre_check.passed == False`, the pipeline continues without intervention.

- [ ] Add a routing function after `context_node` that reads `pre_check.passed`
- [ ] On failure: either return an error response or inject issues as feedback and
      re-run context assembly
- [ ] Add `pre_check_failures` to `ContentResponse.metadata`

---

## 📋 Planned — Long Term

### v7.0.0 — RAG Integration
- [ ] Implement `ContextRetriever` Protocol (stub already defined in `context_builder.py`)
- [ ] Wire retrieval into `context_node` to populate `RETRIEVED CONTEXT` section of prompt
- [ ] Support vector store backend (configurable)

### v7.1.0 — Per-User Style Fingerprinting
- [ ] Implement `StyleFingerprint` Protocol (stub already defined in `context_builder.py`)
- [ ] Learn preferred writing patterns per user from accepted outputs
- [ ] Apply fingerprint as additional entropy constraints

### v7.2.0 — Anthropic Claude Provider
- [ ] Add `anthropic` case to `_make_llm()` in `llm.py`
- [ ] Add Claude model defaults to `_MODEL_DEFAULTS` in `config.py`
- [ ] Add `langchain-anthropic` to `requirements.txt`
- [ ] Update `.env.example` with `ANTHROPIC_API_KEY`

---

## Known Technical Debt

| Item | Severity | Location | Notes |
|---|---|---|---|
| `intent_llm()` / `strategy_llm()` unused | Low | `app/core/llm.py` | Defined; no callers |
| `pre_check` stored but never acted on | Low | `app/workflows/nodes.py` | Inert state key |
| `platform_label` / `style_label` dead code | Low | `app/workflows/content_workflow.py:96-97` | Computed but never consumed |
| Memory stores not persistent | High | `app/services/content_memory.py`, `app/context/failure_memory.py` | In-process only |
| No exception isolation in `memory_node` | Low | `app/workflows/nodes.py` | Side-effect failure fails the request |
| `Any` types on state objects | Low | `app/workflows/state.py` | Loses type safety at graph boundary |
