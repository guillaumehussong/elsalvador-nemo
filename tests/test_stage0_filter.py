from salvador_personas.models.persona import PersonaFilter


def test_filter_department(generator):
    filtered = generator.filter(PersonaFilter(departments=("San Salvador",)))
    assert filtered.count_filtered() == 10
    sample = filtered.sample(3, seed=1)
    assert all(p.department == "San Salvador" for p in sample)
