# Architecture Decisions

> One entry per significant decision. Never delete — mark superseded entries.
> Format: Context → Decision → Alternatives → Tradeoffs.

---

## ADR-001 — Sequential Monolith as Starting Architecture

**Date:** Pre-v5.0.0 (v4.1.0 baseline)
**Status:** Superseded by ADR-002

### Context
The system needed a 13-stage content pipeline with conditional repair branches.
The fastest way to build and validate the domain logic was a single function.

### Decision
Implement the entire pipeline as a sequential `run()` function in
`app/workflows/content_workflow.py`. All intermediate results passed as local
variables. Conditional branches as plain `if` statements.

### Alternatives considered
- LangGraph from the start — rejected as premature; domain logic not yet stable
- Class-based state machine — rejected as heavy for initial iteration

### Tradeoffs
- ✅ Fast to build, easy to debug, linear to read
- ✅ No framework overhead during domain model exploration
- ❌ No formal state contract — intermediate values are implicit
- ❌ Conditional branches buried in function body, not visible as graph structure
- ❌ Not extensible: adding a retry loop required restructuring the entire function
- ❌ Repair ran at most once — `MAX_REPAIR_ATTEMPTS` config var existed but was unused

---

## ADR-002 — Migrate Sequential Pipeline to LangGraph StateGraph

**Date:** 2026-05-27
**Status:** Active

### Context
The sequential monolith had reached the limits of extensibility. Two specific
requirements drove the migration: (1) the repair loop config var
(`MAX_REPAIR_ATTEMPTS`) was planned but unimplementable without restructuring,
(2) future features (human-in-the-loop, persistent checkpointing, parallel stages)
all require a graph model.

### Decision
Convert the sequential `run()` to a LangGraph `StateGraph`. Each of the 13
pipeline stages becomes one graph node. The two `if` repair branches become
`add_conditional_edges`. The public `run()` signature is preserved — routes
call `run(request)` exactly as before.

### Alternatives considered
- **Celery task chain** — would enable async but adds infrastructure dependency;
  overkill when the pipeline is single-request synchronous
- **Custom DAG runner** — rebuild what LangGraph already provides; rejected
- **Keep monolith, add retry loops manually** — creates nested control flow
  that becomes harder to follow and test

### Tradeoffs
- ✅ Conditional branches are explicit graph edges — visible without reading code
- ✅ Retry loops now expressible as graph cycles (not yet wired, but structurally ready)
- ✅ LangGraph checkpointing / human-in-the-loop becomes a config change, not a rewrite
- ✅ Zero changes to any agent file — all `app/agents/*.py` untouched
- ✅ Graph compiles at import time — build errors surface at startup, not at first request
- ❌ `context_package` and result objects are not JSON-serialisable — cannot use
  LangGraph checkpointing without a custom serialiser
- ❌ `total=False` TypedDict means mypy cannot enforce key presence at compile time
- ❌ Module-level `_graph` singleton means the graph cannot be reconfigured per-request

---

## ADR-003 — Pipeline Trace Parity Strategy

**Date:** 2026-05-27
**Status:** Active

### Context
`ContentResponse.pipeline` is a list of `PipelineStage` records consumed by callers.
In the sequential monolith, a "skipped" record was always appended for repair stages
that did not run. With conditional edges, the repair nodes simply do not execute —
leaving the pipeline list shorter than expected.

### Decision
`humanize_validate_node` and `quality_validate_node` each inspect whether the repair
branch will be taken. If not, they append the "skipped" stage record themselves,
before the routing function fires. This ensures the pipeline list is identical
regardless of which path was taken.

### Alternatives considered
- **Pass-through skip node** — an empty node inserted on the bypass path that adds
  the skipped record. Structurally cleaner but adds dead nodes to the graph.
- **Accept shorter pipeline** — break the `ContentResponse` contract; rejected
  because callers depend on consistent stage names.
- **Post-processing in `run()`** — normalize the list after `graph.invoke()`.
  Would work but moves graph concerns out of the graph.

### Tradeoffs
- ✅ `ContentResponse.pipeline` is byte-identical to the pre-migration output
- ✅ No extra nodes in the graph
- ❌ The routing condition is duplicated — once in the routing function, once in the
  validate node. If threshold logic changes, both must be updated together.

---

## ADR-004 — Provider-Agnostic LLM Factory

**Date:** 2026-05-27
**Status:** Active

### Context
The system was originally hardwired to OpenAI via a top-level
`from langchain_openai import ChatOpenAI`. Adding Gemini would have required
editing every LLM call site. Only 2 files actually called the LLM
(`content_generator.py` and `repair_engine.py`), and both went through a factory
in `app/core/llm.py`. The factory was the right abstraction point.

### Decision
- Move the provider import inside `_make_llm()` as a lazy import — chosen provider's
  SDK is only imported if that provider is active
- Return `BaseChatModel` (from `langchain_core`) instead of `ChatOpenAI` from all
  getters — callers only depend on `.invoke()` which is universal
- Add `get_llm(role: str)` as the single named factory function; the four named
  getters (`intent_llm`, `strategy_llm`, `generator_llm`, `repair_llm`) become
  thin wrappers calling `get_llm`
- Add `LLM_PROVIDER` to `config.py` with per-provider model name defaults;
  `os.getenv()` still wins if the user explicitly sets a model var

### Alternatives considered
- **Strategy pattern with Protocol** — cleaner type safety but 4x more files
  for 2 providers; deferred until a third provider is needed
- **Environment-level abstraction (LiteLLM)** — would support any provider but
  adds a heavyweight dependency and bypasses LangChain's tool-binding ecosystem
- **One `llm.py` per provider** — straightforward but callers would need to know
  which module to import from

### Tradeoffs
- ✅ Adding a third provider requires changing exactly one file (`llm.py` `_make_llm`)
- ✅ Zero changes to callers — same getter names, same `.invoke()` interface
- ✅ Lazy imports mean uninstalled provider SDKs don't cause import errors
- ❌ `intent_llm()` and `strategy_llm()` are still unused — intent and strategy stages
  are deterministic; LLM-assisted versions are a future capability
- ❌ No formal Provider Protocol — type checker cannot verify new provider conformance

---

## ADR-005 — WorkflowState TypedDict with `total=False`

**Date:** 2026-05-27
**Status:** Active

### Context
LangGraph's `StateGraph` requires a state type. The pipeline has 9 input fields
and ~20 intermediate fields, all added at different stages. A strictly-typed
state (all required) would require every node to return all keys even if it only
produces one.

### Decision
Use `TypedDict` with `total=False`. Every key is optional. Nodes only return the
keys they produce. LangGraph merges return dicts into the accumulated state.
Non-serialisable objects (`context_package`, `humanization_result`, `validation`)
are typed as `Any` to avoid false type-safety.

### Alternatives considered
- **Pydantic BaseModel** — stricter validation but LangGraph has tighter integration
  with TypedDict; also Pydantic would require every field to have a non-None default
- **Dataclass** — similar to Pydantic but less ecosystem support with LangGraph
- **`total=True` with Optional everywhere** — more verbose, forces all nodes to
  carry all optional fields even when irrelevant

### Tradeoffs
- ✅ Nodes return minimal dicts — easier to read and test
- ✅ State grows naturally as graph executes
- ❌ Missing key access (`state["key"]`) raises `KeyError` at runtime, not at
  type-check time — integration tests are the safety net
- ❌ `Any` types for non-serialisable objects lose type information at the state boundary

---

## ADR-006 — Module-Level `_graph` Singleton

**Date:** 2026-05-27
**Status:** Active

### Context
The `StateGraph` must be compiled before use. Compilation has a small one-time cost
and is deterministic. The compiled graph is stateless — all state lives in the dict
passed to `invoke()`, not in the graph object.

### Decision
Call `build_graph()` once at module import time and assign to `_graph`. All calls
to `content_workflow.run()` share the same compiled graph instance. This mirrors
the existing LLM pool pattern in `app/core/llm.py`.

### Alternatives considered
- **Compile per request** — correct but wasteful; same graph rebuilt on every call
- **Lazy initialization on first request** — avoids import-time cost but delays
  surface of build errors to runtime
- **Pass compiled graph as parameter** — more testable but adds boilerplate to all callers

### Tradeoffs
- ✅ Graph build errors surface at startup — fail fast
- ✅ Zero overhead on hot path (compile once, invoke many)
- ✅ Consistent with existing LLM pool pattern — no new patterns to learn
- ❌ Graph cannot be reconfigured per-request (not currently needed)
- ❌ Hot-reload (e.g. `uvicorn --reload`) causes full graph recompile on each save

---

## ADR-009 — Resilient LLM Provider Chain

**Date:** 2026-05-27
**Status:** Active

### Context
The original `llm.py` bound each role to a single provider at startup. An API key
expiry, quota exhaustion, or temporary network failure would propagate as an unhandled
exception and terminate the request. The pipeline had no way to recover or degrade
gracefully. With multiple providers now supported (OpenAI, Gemini), a fallback path
became viable without significant infrastructure cost.

### Decision
Replace the single-model pool with `ResilientLLM` — an ordered provider chain that
tries each provider up to `LLM_RETRY_ATTEMPTS` times before falling through to the next.
A `_MockProvider` is always appended as the last entry so `.invoke()` never raises,
regardless of provider availability. Structured log lines emit on every attempt,
recording provider, attempt number, latency, and failure reason.

Chain assembly happens once per role at first `get_llm()` call (lazy, same timing as before).
The public API (`intent_llm()`, `generator_llm()`, `repair_llm()`, `repair_llm()`) is preserved;
return type changes from `BaseChatModel` to `ResilientLLM`, which is duck-compatible at all
current call sites (`llm.invoke(prompt)` + `response.content`).

### Alternatives considered
- **Wrap `BaseChatModel` as a subclass** — requires implementing many abstract methods
  (`_generate`, `_llm_type`, etc.). Not worth the complexity for a thin retry wrapper.
- **Retry at the call site (in `content_generator.py` / `repair_engine.py`)** — scatters
  retry logic across multiple files; harder to configure globally.
- **LangChain `with_retry()` / `with_fallbacks()`** — LangChain provides these as chain
  operators but they require `LCEL` chain composition. Our callers use `.invoke()` directly,
  not `|` pipe chains. Adopting LCEL would ripple through every call site.
- **Tenacity library** — good for retries but doesn't handle the provider-switch fallback
  without additional wrapper code. Adds a dependency for functionality we can implement
  in 30 lines.

### Tradeoffs
- ✅ Pipeline never crashes from an LLM failure — worst case is empty content
- ✅ Every call emits structured logs: provider, latency, failure type — full observability
- ✅ Fallback model selection is correct — fallback uses the fallback provider's own
  `MODEL_DEFAULTS`, not the primary provider's model names
- ✅ Public API and call sites unchanged — zero diff in agent files
- ✅ `_MockProvider` is infrastructure-layer safety net, independent of `MOCK_MODE`
- ❌ `ResilientLLM.invoke()` return type is `Any` — type checker cannot verify `.content`
  on the result; this was already true for `BaseChatModel.invoke()` at call sites
- ❌ If all providers fail repeatedly (exhausting retries), the empty mock content
  will score poorly on all validators — the quality loop will exhaust `MAX_REPAIR_ATTEMPTS`
  and surface an empty final output. The pipeline completes but the content is not useful.
- ❌ The mock-provider log message ("all real providers failed") is at ERROR level,
  which may trigger alerts in production monitoring setups. This is intentional.

---

## ADR-008 — Bounded Quality Repair Loop with Convergence Detection

**Date:** 2026-05-27
**Status:** Active

### Context
`MAX_REPAIR_ATTEMPTS` (default: 2) was defined in `config.py` since v5.0.0 but the
graph had a single `quality_repair → format` edge — repair could only run once regardless
of the config. Re-validation after repair was therefore impossible: a repair that
introduced a new quality issue would never be detected.

### Decision
Change `quality_repair → format` to `quality_repair → quality_validate` so the
existing conditional edge on `quality_validate` can decide whether to loop or exit.
Add three loop-control fields to `WorkflowState`:

- `repair_attempt_count` (int) — incremented by `quality_repair_node` each pass
- `previous_quality_score` (Optional[int]) — score before the most recent repair,
  stored by `quality_repair_node` for the convergence check
- `convergence_reached` (bool) — set by `quality_validate_node` when new score ≤ previous

`route_quality()` exits the loop if any of four conditions holds:
score is acceptable, no failures remain, budget is exhausted, or convergence is detected.

### Alternatives considered
- **Separate `route_after_repair()` function** — evaluated but redundant; the existing
  `route_quality` already handles all exit conditions, so funnelling through it from
  both entry points (first validate + re-validate) is simpler
- **Loop counter in `route_quality` only** — routing functions cannot modify state
  in LangGraph, so the counter must live in a node; `quality_repair_node` is the only
  node that executes exactly once per loop iteration
- **Convergence in routing function** — routing functions cannot read state keys set
  by the current node in the same turn; convergence detection must happen inside a node
  so the result is available to the routing function via the merged state

### Tradeoffs
- ✅ `MAX_REPAIR_ATTEMPTS` is now fully enforced with zero config changes
- ✅ Convergence detection prevents infinite loops even if `MAX_REPAIR_ATTEMPTS` is high
- ✅ Pipeline trace shows per-iteration scores and deltas — full observability
- ✅ No changes to agent files, schema, or public `run()` interface
- ✅ Fast path (no repair) is byte-identical to v5.1.0 — skip record parity maintained
- ❌ `quality_validate_node` is now called N+1 times per request (N = loop iterations)
  — adds LLM-free deterministic overhead; acceptable for N ≤ 2
- ❌ Pipeline list rebuilds on every node call — O(N·stages) list copies; negligible
  for N ≤ 2 but worth noting for very high `MAX_REPAIR_ATTEMPTS` values
- ❌ Convergence check duplicates the score comparison in `route_quality`
  (same information expressed in two places); kept because routing functions cannot
  set state and the flag is needed in the response metadata

---

## ADR-007 — Separate `context_node` for Stages 3d and 4

**Date:** 2026-05-27
**Status:** Active

### Context
Stage 4 ("Prompt Optimization") was never a function in the original codebase — it
was an inline log statement that ran immediately after Stage 3d
(`build_generation_prompt_with_context`). Both stages have the same input and output:
the `ContextPackage` and the serialized prompt string.

### Decision
Co-locate both stages in a single `context_node`. The node emits two `PipelineStage`
records: `context_assembly` and `prompt_optimizer`. From the graph's perspective
these are one atomic unit.

### Alternatives considered
- **Split into two nodes** — adds a node that only adds a log record with no
  computation; pure overhead with no benefit

### Tradeoffs
- ✅ Node count stays at 13, matching the 13 original pipeline stages
- ✅ No "thin" nodes that exist only to emit a stage record
- ❌ Stage 3d and Stage 4 cannot be independently retried or inspected via graph tooling
