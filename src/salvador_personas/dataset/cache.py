from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

DATASET_ID = "nvidia/Nemotron-Personas-El-Salvador"
SCHEMA_VERSION = "enriched_v1"


def project_root() -> Path:
    """Racine du repo (contient pyproject.toml)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("pyproject.toml introuvable — lancer depuis salvador-personas")


def config_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / "config"


def data_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / "data"


def hf_cache_dir(root: Path | None = None) -> Path:
    return data_dir(root) / "hf"


def processed_dir(root: Path | None = None) -> Path:
    return data_dir(root) / "processed"


def enriched_parquet_path(root: Path | None = None) -> Path:
    return processed_dir(root) / "personas_enriched.parquet"


def build_meta_path(root: Path | None = None) -> Path:
    return processed_dir(root) / "build_meta.json"


def runs_dir(root: Path | None = None) -> Path:
    return data_dir(root) / "runs"


def load_yaml(name: str, root: Path | None = None) -> dict[str, Any]:
    path = config_dir(root) / name
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def config_hashes(root: Path | None = None) -> dict[str, str]:
    root = root or project_root()
    names = ("derived_fields.yaml", "occupation_roles.yaml", "narrative_tags.yaml")
    return {name: file_sha256(config_dir(root) / name) for name in names}


def dir_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def read_build_meta(root: Path | None = None) -> dict[str, Any]:
    path = build_meta_path(root)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_build_meta(meta: dict[str, Any], root: Path | None = None) -> Path:
    path = build_meta_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def merge_build_meta(updates: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    meta = read_build_meta(root)
    meta.update(updates)
    meta["updated_at"] = datetime.now(UTC).isoformat()
    write_build_meta(meta, root)
    return meta
