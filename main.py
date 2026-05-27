"""
AI Content Orchestration Engine — Entry Point

Quick start:
    uvicorn main:app --reload               # development
    uvicorn main:app --host 0.0.0.0 --port 8000   # production

Alternatively (explicit app package path):
    uvicorn app.main:app --reload

API docs auto-generated at: http://localhost:8000/docs
"""

from app.main import app  # noqa: F401  re-exported for uvicorn main:app
