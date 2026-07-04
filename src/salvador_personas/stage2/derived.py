from __future__ import annotations

import fnmatch
import hashlib
import json
import math
from typing import Any

from salvador_personas.models.persona import EconomicRole


def age_factor(age: int, peak: float, width: float, floor: float) -> float:
    return floor + (1.0 - floor) * math.exp(-((age - peak) ** 2) / (2.0 * width**2))


def stable_noise(uuid: str, std: float) -> float:
    digest = hashlib.md5(uuid.encode(), usedforsecurity=False).hexdigest()
    unit = int(digest[:8], 16) / 0xFFFFFFFF
    return (unit * 2.0 - 1.0) * std


def classify_occupation(occupation: str, roles_cfg: dict[str, Any]) -> EconomicRole:
    overrides = roles_cfg.get("overrides") or {}
    if occupation in overrides:
        return overrides[occupation]

    patterns = roles_cfg.get("patterns") or {}
    for role in ("inactive", "merchant"):
        for pattern in patterns.get(role, []):
            if fnmatch.fnmatchcase(occupation.lower(), pattern.lower()):
                return role  # type: ignore[return-value]

    default = (roles_cfg.get("defaults") or {}).get("unmatched", "consumer")
    return default  # type: ignore[return-value]


def keyword_score(text: str, keywords: list[str]) -> tuple[float, list[str]]:
    if not keywords:
        return 0.0, []
    haystack = text.lower()
    matched = [kw for kw in keywords if kw.lower() in haystack]
    score = len(matched) / max(3, len(keywords))
    return min(1.0, score), matched


def parse_hobbies_text(
    hobbies: str,
    hobbies_list_raw: str,
    tags_cfg: dict[str, Any],
) -> tuple[float, tuple[str, ...]]:
    list_text = hobbies
    if hobbies_list_raw:
        try:
            items = json.loads(hobbies_list_raw)
            if isinstance(items, list):
                list_text = hobbies + " " + " ".join(str(x) for x in items)
        except json.JSONDecodeError:
            list_text = hobbies + " " + hobbies_list_raw

    digital_kws = tags_cfg.get("digital_keywords") or []
    consumption_kws = tags_cfg.get("consumption_keywords") or []

    digital_score, _ = keyword_score(list_text, digital_kws)
    _, consumption_matched = keyword_score(list_text, consumption_kws)
    return digital_score, tuple(consumption_matched)


def compute_income(
    uuid: str,
    age: int,
    education: str,
    occupation: str,
    area: str,
    derived_cfg: dict[str, Any],
) -> float:
    income_cfg = derived_cfg["income"]
    base = float((income_cfg["base_by_education"] or {}).get(education, 300))
    occ_mults = income_cfg.get("occupation_multipliers") or {}
    occ_mult = float((occ_mults.get("overrides") or {}).get(occupation, occ_mults.get("default", 1.0)))
    area_mult = float((income_cfg.get("area_multiplier") or {}).get(area, 1.0))
    curve = income_cfg.get("age_curve") or {}
    factor = age_factor(
        age,
        peak=float(curve.get("peak", 45)),
        width=float(curve.get("width", 15)),
        floor=float(curve.get("floor", 0.6)),
    )
    noise = stable_noise(uuid, float(income_cfg.get("noise_std", 0.08)))
    return max(0.0, base * occ_mult * area_mult * factor * (1.0 + noise))


def compute_adoption_propensity(
    age: int,
    education: str,
    area: str,
    digital_score: float,
    derived_cfg: dict[str, Any],
) -> float:
    adoption_cfg = derived_cfg["adoption"]
    weights = adoption_cfg.get("weights") or {}
    edu_scores = adoption_cfg.get("education_score") or {}
    area_scores = adoption_cfg.get("area_score") or {}
    curve = adoption_cfg.get("age_curve") or {}
    clamp = adoption_cfg.get("clamp") or [0.05, 0.95]

    age_component = age_factor(
        age,
        peak=float(curve.get("peak", 32)),
        width=float(curve.get("width", 12)),
        floor=float(curve.get("floor", 0.3)),
    )
    edu_component = float(edu_scores.get(education, 0.4))
    area_component = float(area_scores.get(area, 0.5))

    raw = (
        float(weights.get("digital_score", 0.35)) * digital_score
        + float(weights.get("education", 0.25)) * edu_component
        + float(weights.get("age", 0.20)) * age_component
        + float(weights.get("area", 0.20)) * area_component
    )
    return max(float(clamp[0]), min(float(clamp[1]), raw))


def build_backstory(persona: str, professional: str, cultural: str) -> str:
    parts = [persona.strip(), f"Contexto profesional: {professional.strip()}"]
    if cultural.strip():
        parts.append(f"Antecedentes culturales: {cultural.strip()}")
    return "\n\n".join(p for p in parts if p)
