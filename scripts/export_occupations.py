#!/usr/bin/env python3
"""Exporte la liste des occupations uniques pour review occupation_roles.yaml."""
import json
import sys
from pathlib import Path

import polars as pl

from salvador_personas.dataset.cache import enriched_parquet_path, project_root


def main() -> None:
    path = enriched_parquet_path()
    if not path.exists():
        print("Cache enrichi absent. Lancer sv-preload d'abord.", file=sys.stderr)
        sys.exit(1)

    occs = (
        pl.scan_parquet(path)
        .select("occupation")
        .unique()
        .sort("occupation")
        .collect()["occupation"]
        .to_list()
    )
    out = project_root() / "data" / "occupations_unique.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(occs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(occs)} occupations → {out}")


if __name__ == "__main__":
    main()
