from __future__ import annotations

import polars as pl

from salvador_personas.models.persona import PersonaFilter


def apply_filter_expr(df: pl.LazyFrame, filt: PersonaFilter | None) -> pl.LazyFrame:
    if filt is None:
        return df
    out = df
    if filt.departments:
        out = out.filter(pl.col("department").is_in(list(filt.departments)))
    if filt.municipalities:
        out = out.filter(pl.col("municipality").is_in(list(filt.municipalities)))
    if filt.occupations:
        out = out.filter(pl.col("occupation").is_in(list(filt.occupations)))
    if filt.age_min is not None:
        out = out.filter(pl.col("age") >= filt.age_min)
    if filt.age_max is not None:
        out = out.filter(pl.col("age") <= filt.age_max)
    if filt.area is not None:
        out = out.filter(pl.col("area") == filt.area)
    if filt.sex is not None:
        out = out.filter(pl.col("sex") == filt.sex)
    if filt.income_min is not None:
        out = out.filter(pl.col("income_usd_monthly") >= filt.income_min)
    return out
