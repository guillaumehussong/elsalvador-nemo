from __future__ import annotations

import argparse
import json
import sys

from salvador_personas.dataset.enrich import build_enriched_cache
from salvador_personas.dataset.loader import preload


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the HF dataset and build the enriched cache.")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip build_enriched_cache")
    parser.add_argument("--force-enrich", action="store_true", help="Rebuild the enriched parquet")
    args = parser.parse_args()

    print("Step 1/2 — HuggingFace preload…")
    meta = preload()
    print(json.dumps({k: meta[k] for k in ("row_count", "hf_cache_bytes", "columns") if k in meta}, indent=2))

    if args.skip_enrich:
        print("Enrichment skipped (--skip-enrich).")
        return

    print("Step 2/2 — build enriched cache (may take several minutes)…")
    meta = build_enriched_cache(force=args.force_enrich)
    print(
        json.dumps(
            {k: meta[k] for k in ("row_count", "enriched_bytes", "schema_version") if k in meta},
            indent=2,
        )
    )
    print("Done.")


if __name__ == "__main__":
    main()
