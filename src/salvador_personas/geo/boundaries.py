from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import httpx
import polars as pl
from shapely.geometry import shape
from shapely.ops import unary_union

from salvador_personas.dataset.cache import project_root

GEOB_API = "https://www.geoboundaries.org/api/current/gbOpen/SLV/ADM{level}/"
CACHE_ADM2 = "geoboundaries_slv_adm2.geojson"
CACHE_ADM1 = "geoboundaries_slv_adm1.geojson"


def normalize_name(name: str) -> str:
    s = unicodedata.normalize("NFD", name.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"^departamento de ", "", s)
    return re.sub(r"[^a-z0-9 ]", "", s).strip()


def geo_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / "data" / "geo"


def fetch_geoboundaries(level: int, root: Path | None = None) -> Path:
    root = root or project_root()
    out = geo_dir(root) / (CACHE_ADM2 if level == 2 else CACHE_ADM1)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 1000:
        return out
    meta = httpx.get(GEOB_API.format(level=level), timeout=60).json()
    data = httpx.get(meta["gjDownloadURL"], timeout=120, follow_redirects=True).content
    out.write_bytes(data)
    return out


def load_features(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["features"]


def _dept_for_point(adm1_features: list[dict], lon: float, lat: float) -> str | None:
    from shapely.geometry import Point

    pt = Point(lon, lat)
    for feat in adm1_features:
        if shape(feat["geometry"]).contains(pt):
            return feat["properties"]["shapeName"]
    return None


def _assign_zone(dept_dataset: str, zone: str, lon: float, lat: float, bounds: tuple[float, float, float, float]) -> bool:
    minx, miny, maxx, maxy = bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    mx = (maxx - minx) * 0.12
    my = (maxy - miny) * 0.12
    z = zone.lower()

    if z == "costa":
        return normalize_name(dept_dataset) == normalize_name("La Libertad") and lat <= miny + (maxy - miny) * 0.3
    if z == "norte":
        return lat >= cy + my
    if z == "sur":
        return lat <= cy - my
    if z == "este":
        return lon >= cx + mx
    if z == "oeste":
        return lon <= cx - mx
    if z == "centro":
        return lat > cy - my and lat < cy + my and lon > cx - mx and lon < cx + mx
    return False


def _zone_for_point(dept_dataset: str, lon: float, lat: float, bounds: tuple[float, float, float, float]) -> str:
    for zone in ("Costa", "Norte", "Sur", "Este", "Oeste", "Centro"):
        if _assign_zone(dept_dataset, zone, lon, lat, bounds):
            return zone
    return "Centro"


def build_reform_municipality_polygons(
    root: Path | None = None,
) -> tuple[dict[str, object], list[str]]:
    root = root or project_root()
    adm1_feats = load_features(fetch_geoboundaries(1, root))
    adm2_feats = load_features(fetch_geoboundaries(2, root))

    dataset_depts = (
        pl.scan_parquet(root / "data/processed/personas_enriched.parquet")
        .select("department")
        .unique()
        .collect()["department"]
        .to_list()
    )
    dept_by_norm = {normalize_name(d): d for d in dataset_depts}

    dept_bounds: dict[str, tuple[float, float, float, float]] = {}
    dept_norm_bounds: dict[str, tuple[float, float, float, float]] = {}
    for feat in adm1_feats:
        geom = shape(feat["geometry"])
        dn = normalize_name(feat["properties"]["shapeName"])
        dept_bounds[feat["properties"]["shapeName"]] = geom.bounds
        if dn in dept_by_norm:
            dept_norm_bounds[dept_by_norm[dn]] = geom.bounds

    buckets: dict[str, list] = {}

    for feat in adm2_feats:
        geom = shape(feat["geometry"])
        c = geom.centroid
        dept_geo = _dept_for_point(adm1_feats, c.x, c.y)
        if not dept_geo:
            continue
        dept_dataset = dept_by_norm.get(normalize_name(dept_geo))
        if not dept_dataset:
            continue
        bounds = dept_norm_bounds[dept_dataset]
        zone = _zone_for_point(dept_dataset, c.x, c.y, bounds)
        key = f"{dept_dataset} {zone}"
        buckets.setdefault(key, []).append(geom)

    municipios = (
        pl.scan_parquet(root / "data/processed/personas_enriched.parquet")
        .select("municipality")
        .unique()
        .collect()["municipality"]
        .to_list()
    )

    polygons: dict[str, object] = {}
    unmatched: list[str] = []
    for muni in municipios:
        polys = buckets.get(muni, [])
        if not polys:
            unmatched.append(muni)
            continue
        polygons[muni] = unary_union(polys)

    # Fallback : secteur bbox ∩ département pour municipios reform sans ADM2 assigné
    from shapely.geometry import box

    for muni in list(unmatched):
        parts = muni.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        dept, zone = parts[0], parts[1]
        if dept not in dept_norm_bounds:
            continue
        minx, miny, maxx, maxy = dept_norm_bounds[dept]
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        if zone == "Norte":
            sector = box(minx, cy, maxx, maxy)
        elif zone == "Sur":
            sector = box(minx, miny, maxx, cy)
        elif zone == "Este":
            sector = box(cx, miny, maxx, maxy)
        elif zone == "Oeste":
            sector = box(minx, miny, cx, maxy)
        elif zone == "Costa":
            sector = box(minx, miny, maxx, miny + (maxy - miny) * 0.35)
        else:
            sector = box(minx + (maxx - minx) * 0.25, miny + (maxy - miny) * 0.25,
                          maxx - (maxx - minx) * 0.25, maxy - (maxy - miny) * 0.25)
        dept_geom = shape(next(f for f in adm1_feats if dept_by_norm.get(normalize_name(f["properties"]["shapeName"])) == dept)["geometry"])
        poly = dept_geom.intersection(sector)
        if not poly.is_empty:
            polygons[muni] = poly
            unmatched.remove(muni)

    return polygons, unmatched
