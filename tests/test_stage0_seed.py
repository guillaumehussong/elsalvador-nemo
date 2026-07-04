def test_sample_seed_reproducible(generator):
    a = [p.uuid for p in generator.sample(5, seed=99)]
    b = [p.uuid for p in generator.sample(5, seed=99)]
    assert a == b

    c = [p.uuid for p in generator.sample(5, seed=42)]
    assert a != c
