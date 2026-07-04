from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from salvador_personas.dataset.cache import enriched_parquet_path, read_build_meta
from salvador_personas.dataset.filters import apply_filter_expr
from salvador_personas.models.persona import (
    DerivedFields,
    NARRATIVE_COLUMNS,
    ParsedTags,
    Persona,
    PersonaFilter,
)


class PersonaGenerator:
    def __init__(self, data_dir: str | None = None) -> None:
        self._root = Path(data_dir) if data_dir else None
        self._parquet = enriched_parquet_path(self._root)
        self._filter: PersonaFilter | None = None
        if not self._parquet.exists():
            raise FileNotFoundError(
                f"Cache enrichi absent : {self._parquet}\n"
                "Lancer : sv-preload (ou python scripts/preload_dataset.py && "
                "python scripts/build_enriched_cache.py)"
            )

    @property
    def row_count(self) -> int:
        meta = read_build_meta(self._root)
        if "row_count" in meta:
            return int(meta["row_count"])
        return pl.scan_parquet(self._parquet).select(pl.len()).collect().item()

    def filter(self, f: PersonaFilter) -> PersonaGenerator:
        clone = PersonaGenerator(str(self._root) if self._root else None)
        clone._filter = f
        return clone

    def count_filtered(self) -> int:
        lf = apply_filter_expr(pl.scan_parquet(self._parquet), self._filter)
        return lf.select(pl.len()).collect().item()

    def sample(self, n: int, *, seed: int | None = None) -> list[Persona]:
        available = self.count_filtered()
        if n > available:
            raise ValueError(f"Demande {n} personas mais seulement {available} disponibles")
        lf = apply_filter_expr(pl.scan_parquet(self._parquet), self._filter)
        sampled = lf.collect().sample(n=n, seed=seed, shuffle=True)
        return [_row_to_persona(row) for row in sampled.iter_rows(named=True)]

    def get(self, uuid: str) -> Persona | None:
        lf = apply_filter_expr(pl.scan_parquet(self._parquet), self._filter)
        rows = lf.filter(pl.col("uuid") == uuid).collect()
        if rows.is_empty():
            return None
        return _row_to_persona(rows.row(0, named=True))


def _row_to_persona(row: dict) -> Persona:
    narratives = {col: str(row.get(col) or "") for col in NARRATIVE_COLUMNS if col in row}
    consumption_raw = row.get("consumption_tags_json") or "[]"
    try:
        consumption = tuple(json.loads(consumption_raw))
    except json.JSONDecodeError:
        consumption = ()

    return Persona(
        uuid=str(row["uuid"]),
        sex=str(row["sex"]),
        age=int(row["age"]),
        marital_status=str(row["marital_status"]),
        household_type=str(row["household_type"]),
        education_level=str(row["education_level"]),
        occupation=str(row["occupation"]),
        area=str(row["area"]),
        municipality=str(row["municipality"]),
        department=str(row["department"]),
        languages_spoken=str(row["languages_spoken"]),
        narratives=narratives,
        backstory=str(row["backstory"]),
        tags=ParsedTags(digital_score=float(row["digital_score"]), consumption_tags=consumption),
        derived=DerivedFields(
            income_usd_monthly=float(row["income_usd_monthly"]),
            economic_role=row["economic_role"],
            adoption_propensity=float(row["adoption_propensity"]),
        ),
    )
