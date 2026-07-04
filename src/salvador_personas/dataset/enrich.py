from __future__ import annotations

import json

import polars as pl

from salvador_personas.dataset.cache import (
    config_hashes,
    dir_size_bytes,
    enriched_parquet_path,
    load_yaml,
    merge_build_meta,
    processed_dir,
    project_root,
    SCHEMA_VERSION,
)
from salvador_personas.models.persona import NARRATIVE_COLUMNS, STRUCTURED_COLUMNS
from salvador_personas.stage2.derived import (
    build_backstory,
    classify_occupation,
    compute_adoption_propensity,
    compute_income,
    parse_hobbies_text,
)


def _load_hf_as_polars(root):
    import os

    from datasets import load_dataset

    from salvador_personas.dataset.cache import DATASET_ID, hf_cache_dir

    hf_dir = hf_cache_dir(root)
    cache_dir = str(hf_dir / "datasets")
    prev = os.environ.get("HF_HOME")
    os.environ["HF_HOME"] = str(hf_dir)
    try:
        ds = load_dataset(DATASET_ID, split="train", cache_dir=cache_dir)
        return pl.from_arrow(ds.data.table)
    finally:
        if prev is None:
            os.environ.pop("HF_HOME", None)
        else:
            os.environ["HF_HOME"] = prev


def build_enriched_cache(root=None, *, force: bool = False) -> dict:
    root = root or project_root()
    out_path = enriched_parquet_path(root)
    if out_path.exists() and not force:
        meta = merge_build_meta(
            {"enriched_bytes": dir_size_bytes(out_path), "schema_version": SCHEMA_VERSION},
            root,
        )
        return meta

    derived_cfg = load_yaml("derived_fields.yaml", root)
    roles_cfg = load_yaml("occupation_roles.yaml", root)
    tags_cfg = load_yaml("narrative_tags.yaml", root)

    df = _load_hf_as_polars(root)

    rows: list[dict] = []
    total = df.height
    for i, record in enumerate(df.iter_rows(named=True)):
        if i > 0 and i % 10000 == 0:
            print(f"  enrich… {i}/{total}")
        uuid = record["uuid"]
        hobbies = record.get("hobbies_and_interests") or ""
        hobbies_list = record.get("hobbies_and_interests_list") or ""
        digital_score, consumption_tags = parse_hobbies_text(hobbies, hobbies_list, tags_cfg)
        occupation = record["occupation"]
        education = record["education_level"]
        area = record["area"]
        age = int(record["age"])

        income = compute_income(uuid, age, education, occupation, area, derived_cfg)
        role = classify_occupation(occupation, roles_cfg)
        adoption = compute_adoption_propensity(age, education, area, digital_score, derived_cfg)
        backstory = build_backstory(
            record.get("persona") or "",
            record.get("professional_persona") or "",
            record.get("cultural_background") or "",
        )

        row = {col: record.get(col) for col in STRUCTURED_COLUMNS if col in record}
        for col in NARRATIVE_COLUMNS:
            if col in record:
                row[col] = record[col]
        row.update(
            {
                "backstory": backstory,
                "digital_score": digital_score,
                "consumption_tags_json": json.dumps(list(consumption_tags), ensure_ascii=False),
                "income_usd_monthly": income,
                "economic_role": role,
                "adoption_propensity": adoption,
            }
        )
        rows.append(row)

    enriched = pl.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.write_parquet(out_path)

    meta = merge_build_meta(
        {
            "row_count": enriched.height,
            "enriched_bytes": dir_size_bytes(out_path),
            "schema_version": SCHEMA_VERSION,
            "config_hashes": config_hashes(root),
            "enriched_complete": True,
        },
        root,
    )
    return meta
