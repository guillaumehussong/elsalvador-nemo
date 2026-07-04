from salvador_personas.stage2.derived import build_backstory, compute_income


def test_backstory_compact():
    text = build_backstory("Yo soy Juan.", "Vendo pupusas.", "Salvadoreño.")
    assert "Yo soy Juan." in text
    assert "Contexto profesional: Vendo pupusas." in text
    assert "Antecedentes culturales:" in text
    assert "Contexto familiar" not in text


def test_income_urban_bachillerato_can_reach_minimum():
    derived_cfg = {
        "income": {
            "base_by_education": {"bachillerato": 420},
            "occupation_multipliers": {"default": 1.0, "overrides": {}},
            "area_multiplier": {"urbano": 1.12, "rural": 0.88},
            "age_curve": {"peak": 45, "width": 15, "floor": 0.6},
            "noise_std": 0.0,
        }
    }
    income = compute_income(
        "uuid-test",
        age=45,
        education="bachillerato",
        occupation="Comercio al por menor",
        area="urbano",
        derived_cfg=derived_cfg,
    )
    assert income >= 365
