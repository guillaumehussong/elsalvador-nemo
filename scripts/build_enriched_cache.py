#!/usr/bin/env python3
"""Construit personas_enriched.parquet (parse narratifs 1×)."""
import argparse

from salvador_personas.dataset.enrich import build_enriched_cache

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    meta = build_enriched_cache(force=args.force)
    print("enrich OK — row_count:", meta.get("row_count"), "enriched_bytes:", meta.get("enriched_bytes"))
