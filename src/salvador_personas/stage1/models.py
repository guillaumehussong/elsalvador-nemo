from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PersonaReaction(BaseModel):
    sentiment: Literal["positivo", "neutral", "negativo"]
    interest_score: int = Field(ge=1, le=10)
    objections: list[str] = Field(default_factory=list)
    verbatim: str

    @field_validator("objections", mode="before")
    @classmethod
    def _coerce_objections(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v.strip() else []
        return list(v)


class FocusGroupPersonaResult(BaseModel):
    persona_label: str
    uuid: str
    age: int
    sex: str
    municipality: str
    department: str
    occupation: str
    reaction: PersonaReaction
    usage: dict[str, int] | None = None


class FocusGroupAggregate(BaseModel):
    mean_interest_score: float
    sentiment_counts: dict[str, int]
    top_objections: list[str]
    sample_verbatims: list[str]


class FocusGroupRun(BaseModel):
    stimulus: str
    model: str
    n: int
    seed: int | None
    personas: list[FocusGroupPersonaResult]
    aggregate: FocusGroupAggregate
    cost_estimate_usd: float | None = None
    cost_actual_usd: float | None = None
    total_tokens: int | None = None
