from __future__ import annotations

import json

from pydantic import ValidationError

from salvador_personas.stage1.parse import extract_json_object

from salvador_personas.models.persona import Persona
from salvador_personas.stage1.aggregate import aggregate_results
from salvador_personas.stage1.cost import estimate_run_cost_usd, usage_to_cost_usd
from salvador_personas.stage1.llm.base import LLMClient
from salvador_personas.stage1.models import (
    FocusGroupAggregate,
    FocusGroupPersonaResult,
    FocusGroupRun,
    PersonaReaction,
)
from salvador_personas.stage1.prompts import SYSTEM_PROMPT, build_user_prompt


def _parse_reaction(raw: str) -> PersonaReaction:
    data = extract_json_object(raw)
    return PersonaReaction.model_validate(data)


def run_focus_group(
    *,
    client: LLMClient,
    personas: list[Persona],
    stimulus: str,
    seed: int | None = None,
) -> FocusGroupRun:
    cost_est = estimate_run_cost_usd(personas, stimulus)
    results: list[FocusGroupPersonaResult] = []
    total_prompt = 0
    total_completion = 0

    for i, persona in enumerate(personas):
        label = chr(ord("A") + i) if i < 26 else str(i + 1)
        user = build_user_prompt(persona, stimulus, label)

        last_error: Exception | None = None
        reaction: PersonaReaction | None = None
        usage_dict: dict[str, int] | None = None

        for attempt in range(2):
            try:
                result = client.complete(system=SYSTEM_PROMPT, user=user, json_mode=True)
                reaction = _parse_reaction(result.content)
                if result.usage:
                    usage_dict = {
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    }
                    total_prompt += result.usage.prompt_tokens
                    total_completion += result.usage.completion_tokens
                break
            except (json.JSONDecodeError, ValidationError, KeyError) as exc:
                last_error = exc
                user = user + "\n\nERROR: JSON inválido. Devuelve solo JSON con las claves requeridas."

        if reaction is None:
            raise RuntimeError(f"Persona {label} : échec parsing LLM") from last_error

        results.append(
            FocusGroupPersonaResult(
                persona_label=label,
                uuid=persona.uuid,
                age=persona.age,
                sex=persona.sex,
                municipality=persona.municipality,
                department=persona.department,
                occupation=persona.occupation,
                reaction=reaction,
                usage=usage_dict,
            )
        )

    agg = aggregate_results(results)
    actual_cost = usage_to_cost_usd(total_prompt, total_completion) if total_prompt else None

    return FocusGroupRun(
        stimulus=stimulus,
        model=client.model,
        n=len(personas),
        seed=seed,
        personas=results,
        aggregate=agg,
        cost_estimate_usd=cost_est["estimated_cost_usd"],
        cost_actual_usd=round(actual_cost, 4) if actual_cost is not None else None,
        total_tokens=total_prompt + total_completion if total_prompt else None,
    )
