import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Provider Selection
# ---------------------------------------------------------------------------
# Which LLM provider to use. Controls model name defaults and which SDK is
# instantiated in llm.py. Valid values: "openai", "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# ---------------------------------------------------------------------------
# Per-provider model name defaults
# Individual model env vars always override these defaults.
# ---------------------------------------------------------------------------
_MODEL_DEFAULTS: dict[str, dict[str, str]] = {
    "openai": {
        "intent":    "gpt-4o-mini",
        "strategy":  "gpt-4o-mini",
        "generator": "gpt-4o-mini",
        "repair":    "gpt-4o-mini",
    },
    "gemini": {
        "intent":    "gemini-2.5-flash",
        "strategy":  "gemini-2.5-flash",
        "generator": "gemini-2.5-pro",
        "repair":    "gemini-2.5-pro",
    },
}

_defaults = _MODEL_DEFAULTS.get(LLM_PROVIDER, _MODEL_DEFAULTS["openai"])

# ---------------------------------------------------------------------------
# LLM Model Selection — each stage can use a different model
# ---------------------------------------------------------------------------
INTENT_MODEL    = os.getenv("INTENT_MODEL",    _defaults["intent"])
STRATEGY_MODEL  = os.getenv("STRATEGY_MODEL",  _defaults["strategy"])
GENERATE_MODEL  = os.getenv("GENERATE_MODEL",  _defaults["generator"])
REPAIR_MODEL    = os.getenv("REPAIR_MODEL",    _defaults["repair"])

# ---------------------------------------------------------------------------
# Temperatures — lower = more deterministic, higher = more creative
# ---------------------------------------------------------------------------
INTENT_TEMPERATURE    = float(os.getenv("INTENT_TEMPERATURE",    "0.0"))
STRATEGY_TEMPERATURE  = float(os.getenv("STRATEGY_TEMPERATURE",  "0.2"))
GENERATE_TEMPERATURE  = float(os.getenv("GENERATE_TEMPERATURE",  "0.7"))
REPAIR_TEMPERATURE    = float(os.getenv("REPAIR_TEMPERATURE",    "0.3"))

# ---------------------------------------------------------------------------
# Pipeline Quality Thresholds
# ---------------------------------------------------------------------------
# Score 0-100. Above PASS_THRESHOLD → content is approved as-is.
VALIDATION_PASS_THRESHOLD = int(os.getenv("VALIDATION_PASS_THRESHOLD", "75"))

# Below AUTO_REPAIR_THRESHOLD → trigger the repair engine.
AUTO_REPAIR_THRESHOLD = int(os.getenv("AUTO_REPAIR_THRESHOLD", "55"))

# Max repair iterations before accepting current output.
MAX_REPAIR_ATTEMPTS = int(os.getenv("MAX_REPAIR_ATTEMPTS", "2"))

# ---------------------------------------------------------------------------
# Humanization Thresholds
# ---------------------------------------------------------------------------
# Score 0-100 from the humanization validator.
# Below HUMANIZATION_REPAIR_THRESHOLD → trigger humanization repair pass.
HUMANIZATION_REPAIR_THRESHOLD = int(os.getenv("HUMANIZATION_REPAIR_THRESHOLD", "60"))
