# Cleanup Report

> Generated: 2026-05-27
> Scope: Full repository analysis — duplicates, dead code, obsolete files, cache artifacts, stale docs
> Status: Analysis only — no files have been modified or deleted

---

## Summary

| Category | Count | Verdict |
|---|---|---|
| Ghost `.pyc` for deleted source files | 6 | Safe to delete |
| Standard `__pycache__` directories | 13 | Safe to delete |
| Dead import (`assemble`) | 1 | Safe to remove |
| Dead variables in `content_workflow.py` | 2 | Safe to remove |
| Unused functions in `prompts.py` | 4 | Review manually |
| Unused LLM getters in `llm.py` | 2 | Must keep (planned use) |
| Stale version strings in `app/main.py` | 3 | Safe to fix |
| Outdated stage counts in docstrings | 3 locations | Safe to fix |
| README.md — OpenAI-only references | 5 lines | Safe to fix |
| README.md — missing LangGraph workflow files | 1 section | Safe to fix |
| README.md — outdated env vars table | 1 table | Safe to fix |
| `LANGGRAPH_MIGRATION.md` — superseded planning doc | 1 file | Review manually |
| Duplicate content (README vs PROJECT_BRAIN) | structural | Review manually |
| Missing `.gitignore` coverage confirmation | verified OK | No action |

---

## 1. Cache Artifacts

### 1a. Ghost `.pyc` files — root `__pycache__/`

These bytecode files correspond to source files that have been deleted from the
working tree. Their source no longer exists; they are pure artifacts.

| Ghost `.pyc` | Deleted source it came from |
|---|---|
| `__pycache__/api.cpython-313.pyc` | `api.py` (root, pre-migration) |
| `__pycache__/app.cpython-313.pyc` | `app.py` (root, pre-migration) — git `D` |
| `__pycache__/app_graph.cpython-313.pyc` | `app_graph.py` (root) — git `D` |
| `__pycache__/config.cpython-313.pyc` | `config.py` (root, pre-migration) |
| `__pycache__/generator.cpython-313.pyc` | `generator.py` (root) — git `D` |
| `__pycache__/state.cpython-313.pyc` | `state.py` (root) — git `D` (NOT `app/workflows/state.py`) |

Note: `__pycache__/main.cpython-313.pyc` is legitimate — `main.py` still exists.

**Verdict: SAFE TO DELETE** — all six files. No source file references them.
**Risk if removed:** None. Python will not regenerate them (source is gone).

---

### 1b. Standard `__pycache__` directories

All 13 `__pycache__` directories under `app/` and `tests/` contain valid bytecode
for current source files. The `.gitignore` already excludes them (`__pycache__/` and
`*.pyc`), so they are not tracked by git.

```
app/__pycache__/
app/agents/__pycache__/
app/api/__pycache__/
app/context/__pycache__/
app/core/__pycache__/
app/knowledge/__pycache__/
app/knowledge/audiences/__pycache__/
app/knowledge/examples/__pycache__/
app/knowledge/platforms/__pycache__/
app/knowledge/styles/__pycache__/
app/schemas/__pycache__/
app/services/__pycache__/
app/workflows/__pycache__/
tests/__pycache__/
```

**Verdict: SAFE TO DELETE** — Python regenerates them automatically on next import.
**Risk if removed:** None. Slightly slower first import after deletion (recompile).
**Note:** These should already be excluded by `.gitignore`. Confirm they are not
committed to the repository before deleting.

---

## 2. Dead Code

### 2a. Dead import: `assemble` in `app/agents/repair_engine.py`

**File:** `app/agents/repair_engine.py` — line 26

```python
from app.core.prompts import bullet_list, assemble
```

`assemble` is imported but **never called anywhere in this file or in any other file
in the codebase**. `bullet_list` IS called (4 times in this file) and must stay.

Search confirmation:
```
grep -rn "assemble(" app/  →  only app/core/prompts.py:28  (the definition itself)
```

**Verdict: SAFE TO REMOVE** the `assemble` name from the import line.
Change to: `from app.core.prompts import bullet_list`
**Risk if removed:** None — the function exists in `prompts.py`, the import is just unnecessary.

---

### 2b. Dead variables in `app/workflows/content_workflow.py`

**File:** `app/workflows/content_workflow.py` — lines 96–97

```python
platform_label = strategy["platform"].get("label", request.use_case)
style_label    = strategy["style"].get("label", "none") if strategy.get("style") else "none"
```

These variables are **computed but never referenced** below those lines.
They are leftover from the pre-LangGraph `run()` where they were used in
`pipeline.append()` calls. After the migration, those calls moved into
`strategy_node` inside `nodes.py`. Both variables became orphaned.

Search confirmation:
```
grep -n "platform_label\|style_label" app/workflows/content_workflow.py
→  96: platform_label = ...
→  97: style_label    = ...
(no other occurrences)
```

**Verdict: SAFE TO REMOVE** both lines.
**Risk if removed:** None — variables are written but never read. Removing them has
zero effect on runtime behaviour.

---

### 2c. Unused functions in `app/core/prompts.py`

`prompts.py` defines 6 functions. Only `bullet_list` has a caller in the codebase.

| Function | Callers |
|---|---|
| `bullet_list()` | `repair_engine.py` lines 115, 116, 232, 233 — **USED** |
| `assemble()` | Imported in `repair_engine.py` but never called — **DEAD** |
| `section()` | Zero callers in entire codebase — **DEAD** |
| `check_list()` | Zero callers in entire codebase — **DEAD** |
| `cross_list()` | Zero callers in entire codebase — **DEAD** |
| `forbidden_phrases()` | Zero callers in entire codebase — **DEAD** |

Search confirmation:
```
grep -rn "section(\|check_list(\|cross_list(\|forbidden_phrases(\|assemble(" app/
→  app/core/prompts.py only (definitions, not calls)
```

**Verdict: REVIEW MANUALLY**
These functions were likely used in an earlier version of the prompt optimizer
before the `ContextPackage` / context engineering layer replaced it. They may
have been intentionally preserved as shared utilities for future use.

- `assemble()` — most likely safe to remove (duplicates `"\n\n".join(...)`)
- `section()`, `check_list()`, `cross_list()`, `forbidden_phrases()` — review
  intent before removing; they may be planned for future agents

**Risk if removed:** Low — no current callers. Medium if a future agent was expected
to use them without explicitly re-implementing them.
**Do NOT remove `bullet_list()`** — it is actively used.

---

### 2d. Unused LLM getters in `app/core/llm.py`

**File:** `app/core/llm.py` — lines 81–82

```python
def intent_llm()    -> BaseChatModel: return get_llm("intent")
def strategy_llm()  -> BaseChatModel: return get_llm("strategy")
```

Neither function has any callers in the codebase. `intent_analyzer.py` and
`strategy_engine.py` are fully deterministic — they never call the LLM.

Search confirmation:
```
grep -rn "intent_llm()\|strategy_llm()" app/
→  app/core/llm.py:9-10  (docstring)
→  app/core/llm.py:81-82  (definitions)
(no call sites)
```

**Verdict: MUST KEEP**
These are documented planned capabilities, not accidental dead code.
`docs/ROADMAP.md` v6.1.0 explicitly plans LLM-assisted intent detection and
LLM-assisted strategy selection. Removing them would require re-adding them
when that work begins.
**Risk if removed:** Low immediately, but would require a re-add at v6.1.0.
The ROADMAP.md and ARCHITECTURE_DECISIONS.md both note their planned use.

---

## 3. Outdated Documentation

### 3a. Version inconsistencies in `app/main.py`

**File:** `app/main.py`

| Line | Current value | Should be |
|---|---|---|
| 2 (docstring) | `v4.0` | `v5.1.0` |
| 24 | `version="4.1.0"` | `version="5.1.0"` |
| 32 | `"version": "4.1.0"` (root endpoint) | `"5.1.0"` |
| 62 | `"version": "4.0.0"` (health endpoint) | `"5.1.0"` |

There are three different version strings in the same file. The current system
version is **5.1.0** per `docs/CHANGELOG.md`.

**Verdict: SAFE TO FIX** — cosmetic but misleading to any consumer of the API
(the `/health` endpoint reports a version 1.1 releases behind actual).

---

### 3b. Stale stage count in docstrings

**File:** `app/api/routes.py` — lines 5, 32
```
POST /generate   → Full 8-stage pipeline           ← was 8, now 13
Full 8-stage content generation pipeline.           ← same issue
```

**File:** `app/main.py` — line 4
```
Entry point for the new modular 8-stage pipeline architecture.   ← now 13-stage
```

**File:** `tests/test_workflow.py` — line 2
```
Integration tests for the 8-stage content pipeline.   ← now 13-stage
```

**Verdict: SAFE TO FIX** — comment-only changes, no runtime impact.

---

### 3c. OpenAI-only references in `README.md`

The README was written before the multi-provider migration (v5.1.0) and contains
five stale OpenAI-specific references:

| Line | Current text | Problem |
|---|---|---|
| 3 | "built with FastAPI, LangChain, and **OpenAI**" | Should mention LangGraph; provider-agnostic |
| 84 | Test command comment references `OPENAI_API_KEY` | Should mention `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| 128 | `OpenAI LLM call` | Should be `LLM call (provider-selectable)` |
| 170 | `# Stage 5 — OpenAI LLM call` | Same |
| 218 | `OPENAI_API_KEY` only in env vars table | Missing `LLM_PROVIDER`, `GOOGLE_API_KEY` |

**Verdict: SAFE TO FIX** — user-facing documentation only.

---

### 3d. Missing LangGraph files in `README.md` project structure

The README project structure section (`app/workflows/`) shows only one file:

```
│   ├── workflows/
│   │   └── content_workflow.py     # Full 13-stage pipeline orchestrator
```

It is missing the three files added in v5.0.0:
- `state.py` — WorkflowState TypedDict
- `nodes.py` — 13 node functions
- `graph.py` — StateGraph builder + compiled singleton

**Verdict: SAFE TO FIX** — user-facing documentation.

---

### 3e. Outdated env vars table in `README.md`

The README env vars table (lines 217–225) is missing three variables added in v5.1.0:
- `LLM_PROVIDER` — the critical provider selection variable
- `GOOGLE_API_KEY` — required for Gemini
- All four model default values shown as `gpt-4o-mini` (no mention of Gemini defaults)

**Verdict: SAFE TO FIX** — user-facing documentation.

---

## 4. Duplicate Documentation

### 4a. `LANGGRAPH_MIGRATION.md` (root) vs `docs/ARCHITECTURE_DECISIONS.md`

**File:** `LANGGRAPH_MIGRATION.md` at root

This was a planning document written **before** the LangGraph migration was
implemented. It describes what to build. Now that v5.0.0 is shipped:

| Section | Status |
|---|---|
| §1 Current Architecture (sequential) | Superseded — now historical |
| §2 Target Architecture | Superseded by ADR-002 |
| §3–4 Files to Create/Modify | Superseded — work is done |
| §5 Files Not Touched | Superseded — confirmed accurate |
| §6 WorkflowState Design | Superseded by `app/workflows/state.py` |
| §7 Node Design | Superseded by `app/workflows/nodes.py` |
| §8–9 Edge/Graph Design | Superseded by `app/workflows/graph.py` |
| §10 Updated content_workflow.py | Superseded by actual file |
| §11 Execution Order table | Still useful as reference |
| §12 Implementation Steps | Historical — work completed |
| §13 Risks & Mitigations | Partially useful; some risks resolved |

**Verdict: REVIEW MANUALLY**
Options:
- **Move to `docs/archive/LANGGRAPH_MIGRATION.md`** — keeps history, removes
  root clutter, makes clear it is superseded
- **Delete** — the ADRs and CHANGELOG capture the decisions; the planning doc
  has no ongoing value
- **Keep at root** — no action required

**Risk if deleted:** Low — all decisions are captured in `docs/ARCHITECTURE_DECISIONS.md`.
The execution order table (§11) is the only section with unique ongoing reference value;
it could be moved to `docs/PROJECT_BRAIN.md` before deleting.

---

### 4b. `README.md` vs `docs/PROJECT_BRAIN.md` — content overlap

Both files contain versions of the same information that have diverged:

| Section | README.md | PROJECT_BRAIN.md | Problem |
|---|---|---|---|
| Project structure | v4.1.0 structure, missing 3 workflow files, no `docs/` dir | Accurate v5.1.0 | README is stale |
| Env vars table | Missing 3 vars, OpenAI-only | Complete and accurate | README is stale |
| Pipeline stages | All 13 stages listed | All 13 nodes listed | Minor wording differences |
| Supported platforms | Accurate | Accurate | OK |
| Supported styles | Accurate | Accurate | OK |

**Verdict: REVIEW MANUALLY — define the boundary**
The right split is:
- `README.md` = user-facing quickstart (install, run, test, basic API examples)
- `docs/PROJECT_BRAIN.md` = authoritative technical reference

Remove the detailed project structure and env vars sections from README or
explicitly point README to PROJECT_BRAIN. Do not maintain both in sync — they will
always drift.

---

## 5. Files Deleted from Working Tree (git status `D`)

These files were deleted from the working tree before this session. Their deletion
is already tracked in git (`D` status). No action is needed on the files themselves —
they are already gone. The items below are noted for completeness.

| Deleted file | Was used for |
|---|---|
| `app.py` (root) | Pre-migration entry point |
| `app_graph.py` (root) | Pre-migration LangGraph prototype |
| `generator.py` (root) | Pre-migration content generator |
| `state.py` (root) | Pre-migration state definition (NOT `app/workflows/state.py`) |
| `templates.py` (root) | Pre-migration prompt templates |
| `archieve/ask_user.py` | Pre-migration human review node |
| `archieve/human_review.py` | Pre-migration human review |
| `archieve/main_old.py` | Archived main entry point |
| `archieve/prompt.txt` | Archived prompt template |
| `archieve/run_agent.py` | Archived agent runner |
| `nodes/__init__.py` | Pre-migration nodes package |
| `nodes/check_quality.py` | Pre-migration quality node |
| `nodes/evaluate.py` | Pre-migration evaluation node |
| `nodes/optimize.py` | Pre-migration optimization node |

**Action:** These deletions should be committed to finalize the cleanup.
Run `git add -u` to stage all tracked deletions, then commit.

**Risk:** None — these files have no callers in the current codebase.

---

## 6. No Issues Found

The following were checked and are clean:

| Item | Result |
|---|---|
| `.gitignore` coverage | Correct — `__pycache__/` and `*.pyc` both excluded |
| `app/api/routes.py` imports | All imports used (note `# noqa: F401` on response types is correct — used as `response_model=`) |
| `main.py` (root) | Clean — single re-export for uvicorn |
| `tests/test_workflow.py` imports | All 6 imports actively used in test classes |
| All `app/**/__init__.py` files | Empty init files — correct for package definition |
| `app/core/config.py` | All constants exported and used |
| `app/workflows/state.py` | Imported by `nodes.py`, `graph.py`, `content_workflow.py` |
| `app/workflows/nodes.py` | All 13 functions imported in `graph.py` |
| `app/workflows/graph.py` | `_graph` imported in `content_workflow.py` |
| `.env.example` | Accurate — matches current config |

---

## Prioritized Action List

### Tier 1 — Safe, zero-risk, do now
1. Delete `__pycache__/api.cpython-313.pyc`, `app.cpython-313.pyc`, `app_graph.cpython-313.pyc`, `config.cpython-313.pyc`, `generator.cpython-313.pyc`, `state.cpython-313.pyc` from root `__pycache__/`
2. Remove `assemble` from the import in `repair_engine.py` line 26
3. Remove lines 96–97 from `content_workflow.py` (`platform_label`, `style_label`)
4. Fix version strings in `app/main.py` (three locations: docstring, FastAPI `version=`, health endpoint)
5. Fix "8-stage" → "13-stage" in `routes.py` (×2) and `app/main.py` (×1) and `tests/test_workflow.py` (×1) docstrings
6. Commit the staged git deletions (`app.py`, `app_graph.py`, `generator.py`, `state.py`, `templates.py`, `archieve/`, `nodes/`)

### Tier 2 — Safe, verify intent first
7. Fix OpenAI-only references in `README.md` (5 locations)
8. Add missing LangGraph workflow files to `README.md` project structure
9. Update env vars table in `README.md`

### Tier 3 — Requires a decision
10. `LANGGRAPH_MIGRATION.md` — move to `docs/archive/` or delete (migration is complete)
11. `app/core/prompts.py` dead functions (`section`, `check_list`, `cross_list`, `forbidden_phrases`, `assemble`) — decide if they are reserved for future use or should be pruned
12. README vs PROJECT_BRAIN boundary — decide how much to keep in README vs reference to docs

### Tier 4 — Must keep (do not touch)
- `intent_llm()` and `strategy_llm()` in `llm.py` — planned for v6.1.0
- All `__pycache__` directories under `app/` — standard runtime artifacts, .gitignored
- `docs/ROADMAP.md` technical debt section — documents the dead code intentionally
