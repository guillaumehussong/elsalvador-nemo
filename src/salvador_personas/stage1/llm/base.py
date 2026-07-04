from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class LLMResult:
    content: str
    usage: LLMUsage | None = None


class LLMClient(Protocol):
    @property
    def model(self) -> str: ...

    def complete(self, *, system: str, user: str, json_mode: bool = True) -> LLMResult: ...
