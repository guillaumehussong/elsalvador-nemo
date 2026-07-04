from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from salvador_personas.dataset.cache import project_root


def load_project_env() -> Path:
    """Charge Hermes puis .env local (local prioritaire)."""
    root = project_root()
    hermes = Path.home() / ".hermes" / ".env"
    if hermes.exists():
        load_dotenv(hermes, override=False)
    load_dotenv(root / ".env", override=True)
    return root


def llm_api_key() -> str:
    base = llm_base_url()
    if "apiyi" in base:
        key = os.getenv("APIYI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    else:
        key = os.getenv("OPENAI_API_KEY") or os.getenv("APIYI_API_KEY") or ""
    return key.strip()


def llm_base_url() -> str:
    return (os.getenv("OPENAI_BASE_URL") or "https://api.apiyi.com/v1").rstrip("/")


def llm_model() -> str:
    return os.getenv("LLM_MODEL") or "claude-haiku-4-5-20251001"
