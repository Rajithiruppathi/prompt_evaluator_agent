# LangGraph Migration Plan

## 1. Current Architecture

The pipeline lives entirely in `app/workflows/content_workflow.py::run()` — a single
sequential function that calls 13 stages one after another, passing intermediate results
through local variables.

```
ContentRequest
    │
    ▼
run(request)   ← content_workflow.py
    │
    ├─ Stage 1  analyze_intent()
    ├─ Stage 2  build_audience_context()
    ├─ Stage 3  build_strategy()
    ├─ Stage 3b select_patterns() + format_experience()
    ├─ Stage 3c get_entropy_directives() + content_memory
    ├─ Stage 3d build_generation_prompt_with_context()
    ├─ Stage 4  [prompt serialization — inline, no function]
    ├─ Stage 5  generate()
    ├─ Stage 5b validate_humanization()
    ├─ Stage 5c repair_humanization()  [conditional]
    ├─ Stage 6  validate()
    ├─ Stage 7  repair()               [conditional]
    ├─ Stage 8  format_output()
    └─ Stage 8b content_memory.register() + failure_memory.record()
    │
    ▼
ContentResponse
```

Conditional branches (currently plain `if` statements):
- After Stage 5b: if `humanization_result.score < HUMANIZATION_REPAIR_THRESHOLD` → run Stage 5c
- After Stage 6:  if `validation.score < AUTO_REPAIR_THRESHOLD and validation.failures` → run Stage 7

---

## 2. Target Architecture

Replace the monolithic `run()` with a `StateGraph`. Each stage becomes a graph **node**.
The two `if` branches become **conditional edges**. The API routes and all agent files
remain completely unchanged.

```
ContentRequest → WorkflowState
    │
    ▼
StateGraph.compile()  ← graph.py
    │
    ├─ node: intent_node
    ├─ node: audience_node
    ├─ node: strategy_node
    ├─ node: experience_node
    ├─ node: entropy_node
    ├─ node: context_node
    ├─ node: generate_node
    ├─ node: humanize_validate_node
    ├─ conditional_edge ──┬─ [score < threshold] → humanize_repair_node
    │                     └─ [score ≥ threshold] → quality_validate_node
    ├─ node: quality_validate_node
    ├─ conditional_edge ──┬─ [score < threshold] → quality_repair_node
    │                     └─ [score ≥ threshold] → format_node
    ├─ node: format_node
    └─ node: memory_node
    │
    ▼
WorkflowState → ContentResponse (assembled in content_workflow.py::run)
```

---

## 3. Files to Create (new)

| File | Purpose |
|------|---------|
| `app/workflows/state.py` | `WorkflowState` TypedDict — all inputs + intermediates |
| `app/workflows/nodes.py` | One node function per stage, each wrapping an existing agent |
| `app/workflows/graph.py` | `build_graph()` — assembles StateGraph, adds edges, compiles |

## 4. Files to Modify (existing)

| File | Change |
|------|--------|
| `app/workflows/content_workflow.py` | Replace sequential body of `run()` with `graph.invoke(state)` + response assembly |

## 5. Files Not Touched

Everything else — all agents, services, context, knowledge, schemas, API routes,
`app/main.py`, `main.py`.

---

## 6. WorkflowState Design

```python
# app/workflows/state.py
from typing import Optional, TypedDict, Any

class WorkflowState(TypedDict, total=False):
    # ── Inputs (from ContentRequest) ─────────────────────────────────────────
    prompt:           str
    use_case:         str
    audience:         str
    goal:             str
    tone:             str
    style:            Optional[str]
    intent_input:     Optional[str]          # request.intent (explicit or None)
    existing_content: Optional[str]
    target_use_case:  Optional[str]

    # ── Stage 1 output ────────────────────────────────────────────────────────
    intent:           str                    # "create" | "improve" | "rewrite" | "convert"

    # ── Stage 2 output ────────────────────────────────────────────────────────
    audience_context: dict                   # {label, knowledge_level, profile}

    # ── Stage 3 output ────────────────────────────────────────────────────────
    strategy:         dict                   # {platform, style, length_target}

    # ── Stage 3b output ───────────────────────────────────────────────────────
    experience_patterns: list[dict]
    experience_block:    str

    # ── Stage 3c output ───────────────────────────────────────────────────────
    entropy_directives: dict
    entropy_block:      str
    memory_directive:   str

    # ── Stage 3d output ───────────────────────────────────────────────────────
    optimized_prompt:  str
    context_package:   Any                   # ContextPackage (not serialisable — held in memory)
    pre_check:         Any                   # PreGenerationCheck result

    # ── Stage 5 output ────────────────────────────────────────────────────────
    draft:             str

    # ── Stage 5b output ───────────────────────────────────────────────────────
    humanization_result: Any                 # HumanizationScore from human_validator

    # ── Stage 5c output ───────────────────────────────────────────────────────
    humanization_repaired: bool
    working_content:       str               # draft, or repaired draft

    # ── Stage 6 output ────────────────────────────────────────────────────────
    validation:        Any                   # ValidationResult

    # ── Stage 7 output ────────────────────────────────────────────────────────
    quality_repaired:  bool
    final:             str                   # working_content after optional repair

    # ── Pipeline trace ────────────────────────────────────────────────────────
    pipeline:          list                  # list[PipelineStage]
```

**Design notes:**

- `total=False` — every key is optional so LangGraph can start with a sparse dict and
  nodes can add keys progressively.
- `Any` types for non-serialisable objects (`context_package`, validation/humanization
  result dataclasses) — these are live objects in memory only; never persisted.
- Input keys (`prompt`, `use_case`, …) mirror `ContentRequest` fields exactly so the
  conversion in `content_workflow.py::run()` is trivial.

---

## 7. Node Design (nodes.py)

Each node has the signature `(state: WorkflowState) -> dict` — it reads what it needs
from `state` and returns a dict of keys to merge back.  No node modifies state in place.

```
intent_node(state)          → {intent, pipeline+=[stage]}
audience_node(state)        → {audience_context, pipeline+=[stage]}
strategy_node(state)        → {strategy, pipeline+=[stage]}
experience_node(state)      → {experience_patterns, experience_block, pipeline+=[stage]}
entropy_node(state)         → {entropy_directives, entropy_block, memory_directive, pipeline+=[stage]}
context_node(state)         → {optimized_prompt, context_package, pre_check, pipeline+=[stage, stage]}
generate_node(state)        → {draft, pipeline+=[stage]}
humanize_validate_node(state) → {humanization_result, working_content, pipeline+=[stage]}
humanize_repair_node(state) → {humanization_result, working_content, humanization_repaired, pipeline+=[stage]}
quality_validate_node(state)→ {validation, pipeline+=[stage]}
quality_repair_node(state)  → {final, quality_repaired, pipeline+=[stage]}
format_node(state)          → {final, pipeline+=[stage]}
memory_node(state)          → {pipeline+=[stage]}   # side-effect only
```

**Immutable pipeline list pattern:**

Because LangGraph merges node return dicts, the list must be rebuilt each time:

```python
def intent_node(state: WorkflowState) -> dict:
    intent = analyze_intent(...)
    stage  = _stage("intent_analysis", "completed", intent_label(intent))
    return {
        "intent":   intent,
        "pipeline": [*state.get("pipeline", []), stage],
    }
```

---

## 8. Conditional Edge Functions (graph.py)

```python
def route_humanization(state: WorkflowState) -> str:
    if state["humanization_result"].score < HUMANIZATION_REPAIR_THRESHOLD:
        return "humanize_repair"
    return "quality_validate"

def route_quality(state: WorkflowState) -> str:
    v = state["validation"]
    if v.score < AUTO_REPAIR_THRESHOLD and v.failures:
        return "quality_repair"
    return "format"
```

---

## 9. Graph Assembly (graph.py)

```python
from langgraph.graph import StateGraph, END

def build_graph():
    g = StateGraph(WorkflowState)

    # ── Nodes ──────────────────────────────────────────────────────────────────
    g.add_node("intent",            intent_node)
    g.add_node("audience",          audience_node)
    g.add_node("strategy",          strategy_node)
    g.add_node("experience",        experience_node)
    g.add_node("entropy",           entropy_node)
    g.add_node("context",           context_node)
    g.add_node("generate",          generate_node)
    g.add_node("humanize_validate", humanize_validate_node)
    g.add_node("humanize_repair",   humanize_repair_node)
    g.add_node("quality_validate",  quality_validate_node)
    g.add_node("quality_repair",    quality_repair_node)
    g.add_node("format",            format_node)
    g.add_node("memory",            memory_node)

    # ── Edges ──────────────────────────────────────────────────────────────────
    g.set_entry_point("intent")
    g.add_edge("intent",            "audience")
    g.add_edge("audience",          "strategy")
    g.add_edge("strategy",          "experience")
    g.add_edge("experience",        "entropy")
    g.add_edge("entropy",           "context")
    g.add_edge("context",           "generate")
    g.add_edge("generate",          "humanize_validate")

    g.add_conditional_edges(
        "humanize_validate",
        route_humanization,
        {"humanize_repair": "humanize_repair", "quality_validate": "quality_validate"},
    )
    g.add_edge("humanize_repair",   "quality_validate")

    g.add_conditional_edges(
        "quality_validate",
        route_quality,
        {"quality_repair": "quality_repair", "format": "format"},
    )
    g.add_edge("quality_repair",    "format")

    g.add_edge("format",            "memory")
    g.add_edge("memory",            END)

    return g.compile()
```

---

## 10. Updated content_workflow.py

`run()` keeps its exact signature and return type.
The only change is the body: build initial state → invoke graph → assemble response.

```python
def run(request: ContentRequest) -> ContentResponse:
    # Build initial state from request
    initial_state: WorkflowState = {
        "prompt":           request.prompt,
        "use_case":         request.use_case,
        "audience":         request.audience,
        "goal":             request.goal,
        "tone":             request.tone,
        "style":            request.style,
        "intent_input":     request.intent,
        "existing_content": request.existing_content,
        "target_use_case":  request.target_use_case,
        "humanization_repaired": False,
        "quality_repaired":      False,
        "pipeline":              [],
    }

    state = _graph.invoke(initial_state)

    # ... assemble ContentResponse from state (same fields, same logic as today)
```

---

## 11. Execution Order — Before vs After

| # | Current (sequential) | LangGraph node | Edge type |
|---|----------------------|----------------|-----------|
| 1 | `analyze_intent()` | `intent` | normal |
| 2 | `build_audience_context()` | `audience` | normal |
| 3 | `build_strategy()` | `strategy` | normal |
| 3b | `select_patterns()` | `experience` | normal |
| 3c | `get_entropy_directives()` | `entropy` | normal |
| 3d | `build_generation_prompt_with_context()` | `context` | normal |
| 4 | _(inline prompt log)_ | _(inside context node)_ | — |
| 5 | `generate()` | `generate` | normal |
| 5b | `validate_humanization()` | `humanize_validate` | normal |
| 5c | `repair_humanization()` if score < 60 | `humanize_repair` | **conditional** |
| 6 | `validate()` | `quality_validate` | normal |
| 7 | `repair()` if score < 55 | `quality_repair` | **conditional** |
| 8 | `format_output()` | `format` | normal |
| 8b | `content_memory.register()` + `failure_memory.record()` | `memory` | normal |

---

## 12. Implementation Steps

1. **Create `app/workflows/state.py`** — WorkflowState TypedDict (new file)
2. **Create `app/workflows/nodes.py`** — one function per node, each importing from existing agents/services (new file)
3. **Create `app/workflows/graph.py`** — `build_graph()` + `_graph = build_graph()` singleton (new file)
4. **Modify `app/workflows/content_workflow.py`** — replace body of `run()` to call `graph.invoke()` and assemble `ContentResponse` from final state

No other files are touched.

---

---

## Phase 2 — Bounded Quality Repair Loop (v5.2.0)

### What changed

The single `quality_repair → format` edge in Phase 1 is replaced with a loop:

```
quality_validate ──► quality_repair ──► quality_validate  (loop)
       │
       └──► format  (exit when any exit condition is met)
```

**Exit conditions (route_quality returns "format"):**
1. `score >= AUTO_REPAIR_THRESHOLD` — quality is acceptable
2. `not failures` — nothing left to fix
3. `repair_attempt_count >= MAX_REPAIR_ATTEMPTS` — budget exhausted
4. `convergence_reached` — repair did not improve the score

### New state fields

| Field | Type | Set by | Purpose |
|---|---|---|---|
| `repair_attempt_count` | `int` | `quality_repair_node` | Loop counter |
| `previous_quality_score` | `Optional[int]` | `quality_repair_node` | Score before this repair, for convergence check |
| `convergence_reached` | `bool` | `quality_validate_node` | True if new score ≤ previous score |

### Convergence diagram

```
quality_validate (visit 1)
    score=48, failures=3
    route_quality → quality_repair
quality_repair (attempt 1)
    previous_score=48, working_content=repaired_v1
    repair_attempt_count=1
quality_validate (visit 2)
    score=52, delta=+4, Re-validation 1/2
    route_quality → quality_repair  (still below threshold)
quality_repair (attempt 2)
    previous_score=52, working_content=repaired_v2
    repair_attempt_count=2
quality_validate (visit 3)
    score=51, delta=-1, Re-validation 2/2, CONVERGED
    route_quality → format  (repair_count=2 >= MAX or convergence)
```

### Response metadata added

```json
{
  "repair_attempt_count": 2,
  "convergence_reached":  true,
  "final_quality_score":  51
}
```

### Files modified in Phase 2

| File | Change |
|---|---|
| `app/workflows/state.py` | +3 loop fields |
| `app/workflows/nodes.py` | `quality_validate_node`: convergence, loop-aware skip; `quality_repair_node`: counter + content update |
| `app/workflows/graph.py` | `route_quality` expanded; `quality_repair → quality_validate` edge |
| `app/workflows/content_workflow.py` | Initial state fields + metadata |

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `context_package` is a live object, not JSON-serialisable | Keep it as `Any` in TypedDict; it only lives in-process — no checkpointing |
| LangGraph state merging overwrites list keys | Return full rebuilt pipeline list from every node (`[*old_pipeline, new_stage]`) |
| Conditional edge routing logic must match current thresholds | Import `AUTO_REPAIR_THRESHOLD` and `HUMANIZATION_REPAIR_THRESHOLD` from `app.core.config` — same source as today |
| `total=False` on TypedDict means mypy won't catch missing keys | Add a small unit test that runs `graph.invoke(minimal_state)` in tests/ |
| Import of `_graph` singleton at module level causes startup cost | Acceptable — same cost as loading LLM clients today |
