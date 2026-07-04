from __future__ import annotations

import json
import os
from typing import Any

from datasets import load_dataset

from salvador_personas.dataset.cache import (
    DATASET_ID,
    dir_size_bytes,
    hf_cache_dir,
    merge_build_meta,
    processed_dir,
)


def preload(root=None) -> dict[str, Any]:
    from salvador_personas.dataset.cache import project_root

    root = root or project_root()
    hf_dir = hf_cache_dir(root)
    hf_dir.mkdir(parents=True, exist_ok=True)
    processed_dir(root).mkdir(parents=True, exist_ok=True)
    cache_dir = str(hf_dir / "datasets")

    prev_env = os.environ.get("HF_HOME")
    os.environ["HF_HOME"] = str(hf_dir)

    try:
        ds = load_dataset(DATASET_ID, split="train", cache_dir=cache_dir)
        row_count = len(ds)
        columns = list(ds.column_names)
    finally:
        if prev_env is None:
            os.environ.pop("HF_HOME", None)
        else:
            os.environ["HF_HOME"] = prev_env

    meta = merge_build_meta(
        {
            "dataset_id": DATASET_ID,
            "row_count": row_count,
            "columns": columns,
            "hf_cache_bytes": dir_size_bytes(hf_dir),
            "hf_cache_dir": str(hf_dir),
            "preload_complete": True,
        },
        root,
    )
    return meta
