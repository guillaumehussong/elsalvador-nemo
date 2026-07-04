from shapely.geometry import Polygon

from salvador_personas.geo.points import TriangleSampler, uuid_seed


def test_uuid_seed_deterministic():
    assert uuid_seed("abc-123") == uuid_seed("abc-123")
    assert uuid_seed("abc-123") != uuid_seed("abc-124")


def test_triangle_sampler_reproducible():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    sampler = TriangleSampler.from_polygon(poly)
    import random

    rng1 = random.Random(42)
    rng2 = random.Random(42)
    p1 = sampler.sample(rng1)
    p2 = sampler.sample(rng2)
    assert p1 == p2
    assert poly.contains(Polygon([p1, p1, p1]).centroid) or poly.boundary.distance(Polygon([p1, p1, p1]).centroid) < 1e-9
