"""
AI Content Orchestration Engine — v4.0

Entry point for the new modular 8-stage pipeline architecture.
Start with: uvicorn app.main:app --reload
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from app.api.routes import router

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_LOG_DATE   = "%H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    datefmt=_LOG_DATE,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(_LOG_DIR / "app.log"), mode="a"),
    ],
)

app = FastAPI(
    title="AI Content Orchestration Engine",
    description=(
        "Production-grade, multi-stage content generation pipeline. "
        "Audience-intelligent · Platform-aware · Style-driven · Auto-validated."
    ),
    version="4.1.0",
)


@app.get("/")
def root():
    return {
        "name": "AI Content Orchestration Engine",
        "version": "4.1.0",
        "pipeline_stages": [
            "1.  Intent Understanding",
            "2.  Audience Intelligence",
            "3.  Use Case Strategy",
            "3b. Experience Pattern Selection",
            "3c. Style Entropy + Content Memory",
            "3d. Context Assembly + Pre-Generation Validation",
            "4.  Prompt Optimization (Context Engine)",
            "5.  Content Generation",
            "5b. Humanization Validation",
            "5c. Humanization Repair",
            "6.  Quality Validation (13 checks)",
            "7.  Quality Auto-Repair",
            "8.  Final Formatting",
            "8b. Memory Registration + Failure Recording",
        ],
        "endpoints": {
            "POST /generate":   "Full pipeline — create, improve, rewrite, or convert content",
            "POST /validate":   "Score existing content (0-100) with structured feedback",
            "GET  /styles":     "List writing style identities",
            "GET  /platforms":  "List supported platforms",
            "GET  /audiences":  "List audience profiles",
            "GET  /health":     "Health check",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "4.1.0"}


app.include_router(router)
