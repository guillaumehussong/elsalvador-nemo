from __future__ import annotations

import argparse
import json
import sys

from salvador_personas.dataset.enrich import build_enriched_cache
from salvador_personas.dataset.loader import preload


def main() -> None:
    parser = argparse.ArgumentParser(description="Télécharge le dataset HF et construit le cache enrichi.")
    parser.add_argument("--skip-enrich", action="store_true", help="Ne pas lancer build_enriched_cache")
    parser.add_argument("--force-enrich", action="store_true", help="Reconstruire le parquet enrichi")
    args = parser.parse_args()

    print("Étape 1/2 — preload HuggingFace…")
    meta = preload()
    print(json.dumps({k: meta[k] for k in ("row_count", "hf_cache_bytes", "columns") if k in meta}, indent=2))

    if args.skip_enrich:
        print("Enrichissement ignoré (--skip-enrich).")
        return

    print("Étape 2/2 — build cache enrichi (peut prendre plusieurs minutes)…")
    meta = build_enriched_cache(force=args.force_enrich)
    print(
        json.dumps(
            {k: meta[k] for k in ("row_count", "enriched_bytes", "schema_version") if k in meta},
            indent=2,
        )
    )
    print("Terminé.")


if __name__ == "__main__":
    main()
