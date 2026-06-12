# AI Content Orchestration Engine

A production-grade, multi-stage AI content generation pipeline built with FastAPI, LangChain, and OpenAI. Generates audience-aware, platform-optimized, humanized content across any format — LinkedIn posts, blog articles, cold emails, ad copy, Twitter threads, SEO articles, and more.

---

## Quickstart

### 1. Activate virtual environment

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
# then edit .env and set OPENAI_API_KEY=sk-...
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

Server starts at **http://localhost:8000**
Auto-generated API docs at **http://localhost:8000/docs**

---

## Test the API

### Generate content

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Why most RAG pipelines fail in production",
    "use_case": "LinkedIn Post",
    "audience": "AI Engineers",
    "tone": "Direct",
    "goal": "Spark conversation about production AI"
  }'
```

### Validate existing content

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your content here...",
    "use_case": "LinkedIn Post"
  }'
```

### List available options

```bash
curl http://localhost:8000/styles      # Writing styles
curl http://localhost:8000/platforms   # Supported platforms
curl http://localhost:8000/audiences   # Audience profiles
curl http://localhost:8000/health      # Health check
```

### Run tests (no API key needed for unit tests)

```bash
pytest tests/ -v -m "not integration"    # unit tests only
pytest tests/ -v                          # all tests (requires OPENAI_API_KEY)
```

### Enable automatic provider fallback

```bash
# Primary: OpenAI → Fallback: Gemini → Last resort: empty mock (never crashes)
LLM_PROVIDER=openai
FALLBACK_PROVIDER=gemini
LLM_RETRY_ATTEMPTS=2   # try each provider twice before advancing
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
```

If OpenAI fails (quota, network, key expiry), the pipeline automatically retries
with Gemini. Every attempt logs `provider`, `latency`, and the failure reason.
If every provider fails, an empty response is returned and logged at ERROR level —
the pipeline never crashes.

---

### Run the full pipeline without any API key

```bash
# In your .env (or inline):
MOCK_MODE=true uvicorn main:app --reload

# Or set in .env file:
echo "MOCK_MODE=true" >> .env
uvicorn main:app --reload
```

Then call `/generate` normally — all 13 pipeline stages execute, no LLM is invoked:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Why RAG pipelines fail in production",
    "use_case": "LinkedIn Post",
    "audience": "AI Engineers",
    "goal": "Educate",
    "tone": "Direct"
  }'
```

The response will contain `"MOCK GENERATED CONTENT: ..."` in `final_output` and a
complete pipeline trace through all stages. Quality and humanization validators run
normally. The repair loop will exhaust `MAX_REPAIR_ATTEMPTS` since no LLM improves
the score — this exercises the convergence exit path.

---

## Request Schema

```json
{
  "prompt":           "Topic or brief",
  "use_case":         "LinkedIn Post | Blog | Cold Email | Ad Copy | Twitter Thread | SEO Article | Technical Post",
  "audience":         "AI Engineers | Startup Founders | Marketers | Developers | Enterprise Buyers | Students",
  "tone":             "Direct | Professional | Conversational | Casual",
  "goal":             "What the content should achieve",
  "style":            "(optional) Technical Educator | Contrarian Expert | Founder Storyteller | Minimalist Operator | Strategic Advisor | Storyteller | Analyst",
  "intent":           "(optional) create | improve | rewrite | convert — auto-detected if omitted",
  "existing_content": "(optional) Content to improve / rewrite / convert",
  "target_use_case":  "(optional) Target platform for convert intent"
}
```

---

## Pipeline — 13 Stages

```
POST /generate
      │
      ▼
┌──────────────────────────────┐
│  1.  Intent Analyzer         │  Detects create / improve / rewrite / convert
├──────────────────────────────┤
│  2.  Audience Engine         │  Loads vocabulary, pain points, trust signals
├──────────────────────────────┤
│  3.  Strategy Engine         │  Platform rules + style selection
├──────────────────────────────┤
│  3b. Experience Patterns     │  Injects production incident / tradeoff patterns
├──────────────────────────────┤
│  3c. Style Entropy + Memory  │  Per-request variation directives + anti-repetition
├──────────────────────────────┤
│  3d. Context Assembly        │  Builds ContextPackage + pre-generation validation
├──────────────────────────────┤
│  4.  Prompt Optimizer        │  Context-engine prompt (few-shot + failure memory)
├──────────────────────────────┤
│  5.  Content Generator       │  LLM call (OpenAI or Gemini — provider-selectable)
├──────────────────────────────┤
│  5b. Humanization Validator  │  Scores specificity, tension, originality, experience
├──────────────────────────────┤
│  5c. Humanization Repair     │  Deterministic + LLM surgical fix if score < threshold
├──────────────────────────────┤
│  6.  Quality Validator       │  13 deterministic checks, score 0-100
├──────────────────────────────┤
│  7.  Quality Auto-Repair     │  Bounded retry loop (MAX_REPAIR_ATTEMPTS) with
│                              │  convergence detection — loops back to validator
├──────────────────────────────┤
│  8.  Formatter               │  Platform-native structure (hashtags, spacing, etc.)
├──────────────────────────────┤
│  8b. Memory Registration     │  Anti-repetition + failure-aware generation
└──────────────────────────────┘
      │
      ▼
  ContentResponse
```

---

## Project Structure

```
prompt_evaluator_agent/
│
├── main.py                         # Entry point → delegates to app/main.py
├── requirements.txt
├── .env.example
├── README.md
│
├── app/
│   ├── main.py                     # FastAPI app definition (v4.1.0)
│   │
│   ├── api/
│   │   └── routes.py               # All endpoints: /generate, /validate, /styles, /platforms, /audiences
│   │
│   ├── agents/                     # Pipeline stage executors
│   │   ├── intent_analyzer.py      # Stage 1 — detect create/improve/rewrite/convert
│   │   ├── audience_engine.py      # Stage 2 — audience profile loader
│   │   ├── strategy_engine.py      # Stage 3 — platform + style strategy
│   │   ├── prompt_optimizer.py     # Stage 4 — context-engine prompt builder
│   │   ├── content_generator.py    # Stage 5 — OpenAI LLM call
│   │   ├── validator.py            # Stage 6 — 13-check quality scorer
│   │   ├── repair_engine.py        # Stage 7 — deterministic + LLM repair
│   │   └── formatter.py            # Stage 8 — platform-native formatting
│   │
│   ├── context/                    # Context Engineering package
│   │   ├── context_builder.py      # ContextPackage — assembles + serializes to prompt
│   │   ├── platform_context.py     # Typed platform rules (LinkedInContext, BlogContext, ...)
│   │   ├── audience_context.py     # Typed audience profiles (EngineerAudienceContext, ...)
│   │   ├── style_context.py        # Typed style behaviors (ContraryExpertStyle, ...)
│   │   ├── examples_context.py     # Few-shot good/bad examples with explanations
│   │   ├── failure_memory.py       # Per-(use_case, audience) failure tracking
│   │   └── banned_phrases.py       # Centralized banned phrase registry
│   │
│   ├── services/                   # Humanization + entropy services
│   │   ├── experience_patterns.py  # 24 production incident/tradeoff patterns
│   │   ├── style_entropy.py        # Per-request variation directives
│   │   ├── human_validator.py      # 4-dimension humanization scorer (0-100)
│   │   └── content_memory.py       # Ring-buffer anti-repetition tracker
│   │
│   ├── knowledge/                  # Static knowledge base (platform/audience/style profiles)
│   │   ├── platforms/profiles.py
│   │   ├── audiences/profiles.py
│   │   ├── styles/profiles.py
│   │   └── examples/content_examples.py
│   │
│   ├── workflows/
│   │   └── content_workflow.py     # Full 13-stage pipeline orchestrator
│   │
│   ├── schemas/
│   │   ├── request.py              # ContentRequest, ValidateRequest
│   │   └── response.py             # ContentResponse, ValidationResult, HumanizationResult
│   │
│   └── core/
│       ├── config.py               # Environment config + thresholds
│       ├── llm.py                  # LLM client factory
│       └── prompts.py              # Prompt assembly utilities
│
└── tests/
    └── test_workflow.py            # Unit + integration tests
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MOCK_MODE` | `false` | `true` → full pipeline runs with no API key |
| `LLM_PROVIDER` | `openai` | Primary provider: `openai` or `gemini` |
| `FALLBACK_PROVIDER` | *(empty)* | Secondary provider if primary fails; `openai` or `gemini` |
| `LLM_RETRY_ATTEMPTS` | `1` | Attempts per provider before falling back |
| `OPENAI_API_KEY` | *(required if openai)* | OpenAI API key |
| `GOOGLE_API_KEY` | *(required if gemini)* | Google AI API key |
| `GENERATE_MODEL` | provider default | Model for content generation |
| `REPAIR_MODEL` | provider default | Model for auto-repair |
| `VALIDATION_PASS_THRESHOLD` | `75` | Quality score required to skip repair |
| `AUTO_REPAIR_THRESHOLD` | `55` | Score below which repair runs |
| `MAX_REPAIR_ATTEMPTS` | `2` | Max quality repair loop iterations |
| `HUMANIZATION_REPAIR_THRESHOLD` | `60` | Humanization score below which repair runs |

---

## Supported Platforms

| Platform | Key |
|---|---|
| LinkedIn Post | `LinkedIn Post` |
| Blog | `Blog` |
| Cold Email | `Cold Email` |
| Ad Copy | `Ad Copy` |
| Twitter Thread | `Twitter Thread` |
| SEO Article | `SEO Article` |
| Technical Post | `Technical Post` |
| Educational Content | `Educational Content` |

## Supported Writing Styles

`Technical Educator` · `Contrarian Expert` · `Founder Storyteller` · `Minimalist Operator` · `Strategic Advisor` · `Storyteller` · `Analyst`
