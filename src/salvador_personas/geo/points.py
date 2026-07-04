from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from shapely.ops import triangulate


@dataclass
class TriangleSampler:
    triangles: list
    cumulative: list[float]
    total_area: float

    @classmethod
    def from_polygon(cls, polygon) -> TriangleSampler:
        tris = []
        areas = []
        for tri in triangulate(polygon):
            if not polygon.contains(tri.representative_point()):
                continue
            a = tri.area
            if a <= 0:
                continue
            tris.append(tri)
            areas.append(a)
        if not tris:
            raise ValueError("No valid triangles for polygon")
        total = sum(areas)
        cumulative = []
        acc = 0.0
        for a in areas:
            acc += a / total
            cumulative.append(acc)
        return cls(triangles=tris, cumulative=cumulative, total_area=total)

    def sample(self, rng: random.Random) -> tuple[float, float]:
        u = rng.random()
        idx = next(i for i, c in enumerate(self.cumulative) if u <= c)
        tri = self.triangles[idx]
        coords = list(tri.exterior.coords)[:3]
        r1, r2 = rng.random(), rng.random()
        sr = r1**0.5
        u1, u2 = 1 - sr, sr * (1 - r2)
        u3 = sr * r2
        lon = u1 * coords[0][0] + u2 * coords[1][0] + u3 * coords[2][0]
        lat = u1 * coords[0][1] + u2 * coords[1][1] + u3 * coords[2][1]
        return lon, lat


def uuid_seed(uuid: str) -> int:
    return int(hashlib.md5(uuid.encode(), usedforsecurity=False).hexdigest(), 16) % (2**32)


def random_point_in_polygon(polygon, uuid: str) -> tuple[float, float]:
    rng = random.Random(uuid_seed(uuid))
    sampler = TriangleSampler.from_polygon(polygon)
    return sampler.sample(rng)
