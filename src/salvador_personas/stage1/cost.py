from __future__ import annotations

import os

from salvador_personas.models.persona import Persona
from salvador_personas.stage1.prompts import SYSTEM_PROMPT, build_user_prompt


def _chars_to_tokens(chars: int) -> int:
    return max(1, chars // 4)


def estimate_tokens_per_call(persona: Persona, stimulus: str) -> tuple[int, int]:
    user = build_user_prompt(persona, stimulus, "A")
    input_tokens = _chars_to_tokens(len(SYSTEM_PROMPT) + len(user))
    output_tokens = int(os.getenv("LLM_EST_OUTPUT_TOKENS", "350"))
    return input_tokens, output_tokens


def price_per_million() -> tuple[float, float]:
    input_p = float(os.getenv("LLM_INPUT_PRICE_PER_1M_USD", "0.80"))
    output_p = float(os.getenv("LLM_OUTPUT_PRICE_PER_1M_USD", "4.00"))
    return input_p, output_p


def estimate_run_cost_usd(personas: list[Persona], stimulus: str) -> dict:
    input_p, output_p = price_per_million()
    total_in = 0
    total_out = 0
    for i, p in enumerate(personas):
        inp, out = estimate_tokens_per_call(p, stimulus)
        total_in += inp
        total_out += out

    cost = (total_in / 1_000_000) * input_p + (total_out / 1_000_000) * output_p
    return {
        "estimated_input_tokens": total_in,
        "estimated_output_tokens": total_out,
        "estimated_total_tokens": total_in + total_out,
        "estimated_cost_usd": round(cost, 4),
        "input_price_per_1m_usd": input_p,
        "output_price_per_1m_usd": output_p,
    }


def usage_to_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    input_p, output_p = price_per_million()
    return (prompt_tokens / 1_000_000) * input_p + (completion_tokens / 1_000_000) * output_p
