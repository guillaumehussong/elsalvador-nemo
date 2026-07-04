from __future__ import annotations

import fnmatch
import json
from pathlib import Path

import numpy as np
import polars as pl

from salvador_personas.dataset.cache import load_yaml, project_root
from salvador_personas.geo.boundaries import build_reform_municipality_polygons
from salvador_personas.geo.points import TriangleSampler, uuid_seed


def classify_occupation(occupation: str, cfg: dict) -> int:
    groups = cfg.get("groups") or {}
    names = [k for k in groups if k != "otro"]
    for i, name in enumerate(names):
        for pattern in groups.get(name, []):
            if fnmatch.fnmatchcase(occupation.lower(), pattern.lower()):
                return i
    return len(names)  # otro


def income_bucket(income: float) -> int:
    return min(9, max(0, int(income / 150)))


def build_map_export(root: Path | None = None) -> dict:
    root = root or project_root()
    out_dir = root / "apps" / "map" / "public" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    occ_cfg = load_yaml("occupation_groups.yaml", root)
    polygons, unmatched = build_reform_municipality_polygons(root)
    if unmatched:
        raise RuntimeError(f"Municipios sans polygone : {unmatched}")

    df = pl.read_parquet(root / "data/processed/personas_enriched.parquet")
    depts = sorted(df["department"].unique().to_list())
    munis = sorted(df["municipality"].unique().to_list())
    occupations = sorted(df["occupation"].unique().to_list())
    dept_id = {d: i for i, d in enumerate(depts)}
    muni_id = {m: i for i, m in enumerate(munis)}
    occ_id = {o: i for i, o in enumerate(occupations)}

    n = df.height
    positions = np.zeros(n * 2, dtype=np.float32)
    attrs = np.zeros(n * 8, dtype=np.uint8)

    samplers: dict[str, TriangleSampler] = {}
    for m in munis:
        samplers[m] = TriangleSampler.from_polygon(polygons[m])

    import random

    for i, row in enumerate(df.iter_rows(named=True)):
        muni = row["municipality"]
        rng = random.Random(uuid_seed(row["uuid"]))
        lon, lat = samplers[muni].sample(rng)
        positions[i * 2] = lon
        positions[i * 2 + 1] = lat
        attrs[i * 8] = dept_id[row["department"]]
        attrs[i * 8 + 1] = muni_id[muni]
        attrs[i * 8 + 2] = 0 if row["sex"] == "Femenino" else 1
        attrs[i * 8 + 3] = 0 if row["area"] == "rural" else 1
        attrs[i * 8 + 4] = min(255, max(0, int(row["age"])))
        attrs[i * 8 + 5] = income_bucket(float(row["income_usd_monthly"]))
        attrs[i * 8 + 6] = classify_occupation(row["occupation"], occ_cfg)
        attrs[i * 8 + 7] = occ_id[row["occupation"]]

    points_path = out_dir / "points.bin"
    attrs_path = out_dir / "attrs.bin"
    positions.tofile(points_path)
    attrs.tofile(attrs_path)

    min_lon, max_lon = float(positions[0::2].min()), float(positions[0::2].max())
    min_lat, max_lat = float(positions[1::2].min()), float(positions[1::2].max())
    bundle_bytes = points_path.stat().st_size + attrs_path.stat().st_size

    ss_dept_id = dept_id.get("San Salvador")
    ss_mask = attrs[0::8] == ss_dept_id if ss_dept_id is not None else None
    if ss_mask is not None and ss_mask.any():
        ss_lons = positions[0::2][ss_mask]
        ss_lats = positions[1::2][ss_mask]
        ss_bounds = [
            float(ss_lons.min()),
            float(ss_lats.min()),
            float(ss_lons.max()),
            float(ss_lats.max()),
        ]
    else:
        ss_bounds = None

    manifest = {
        "version": 1,
        "row_count": n,
        "bounds": [min_lon, min_lat, max_lon, max_lat],
        "bundle_bytes": bundle_bytes,
        "default_scope": "national" if bundle_bytes < 5_000_000 else "san_salvador",
        "san_salvador_dept_id": ss_dept_id,
        "san_salvador_bounds": ss_bounds,
        "departments": depts,
        "municipalities": munis,
        "occupation_groups": [k for k in (occ_cfg.get("groups") or {}) if k != "otro"] + ["otro"],
        "occupations": occupations,
        "sex_labels": ["Femenino", "Masculino"],
        "area_labels": ["rural", "urbano"],
        "attribution": {
            "personas": "NVIDIA / WideLabs — Nemotron-Personas-El-Salvador (CC BY 4.0)",
            "personas_url": "https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador",
            "boundaries": "geoBoundaries (William & Mary, CC BY 4.0)",
            "boundaries_url": "https://www.geoboundaries.org",
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    return manifest
