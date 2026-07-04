#!/usr/bin/env python3
"""Télécharge le dataset et mesure build_meta.json."""
from salvador_personas.dataset.loader import preload

if __name__ == "__main__":
    meta = preload()
    print("preload OK — row_count:", meta.get("row_count"), "hf_cache_bytes:", meta.get("hf_cache_bytes"))
