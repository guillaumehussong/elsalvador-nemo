from __future__ import annotations

import os

from salvador_personas.stage1.llm.base import LLMClient
from salvador_personas.stage1.llm.openai_compat import OpenAICompatClient


def create_llm_client() -> LLMClient:
    client_type = (os.getenv("LLM_CLIENT") or "openai").strip().lower()
    if client_type == "openai":
        return OpenAICompatClient()
    raise ValueError(f"LLM_CLIENT non supporté : {client_type!r} (attendu: openai)")
