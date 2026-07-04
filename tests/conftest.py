from __future__ import annotations

import json
import shutil
from pathlib import Path

import polars as pl
import pytest

from salvador_personas.models.persona import NARRATIVE_COLUMNS, STRUCTURED_COLUMNS


@pytest.fixture(scope="session")
def project_fixture(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("salvador_test")
    shutil.copytree(
        Path(__file__).resolve().parents[1] / "config",
        root / "config",
    )
    processed = root / "data" / "processed"
    processed.mkdir(parents=True)

    rows = []
    departments = ["San Salvador", "La Libertad", "Santa Ana"]
    for i in range(30):
        dept = departments[i % 3]
        rows.append(
            {
                "uuid": f"test-uuid-{i:04d}",
                "sex": "Femenino" if i % 2 == 0 else "Masculino",
                "age": 20 + (i % 40),
                "marital_status": "soltero",
                "household_type": "nuclear",
                "education_level": "bachillerato",
                "occupation": "Actividades de hospitales" if i % 5 == 0 else "Comercio al por menor",
                "area": "urbano" if i % 3 else "rural",
                "municipality": "San Salvador Este" if dept == "San Salvador" else "Santa Tecla",
                "department": dept,
                "languages_spoken": "español",
                "country": "El Salvador",
                "persona": f"Soy persona {i}.",
                "professional_persona": f"Trabajo en sector {i}.",
                "cultural_background": f"Cultura {i}.",
                "sports_persona": "",
                "arts_persona": "",
                "travel_persona": "",
                "culinary_persona": "",
                "family_persona": "",
                "skills_and_expertise": "",
                "skills_and_expertise_list": "[]",
                "hobbies_and_interests": "redes sociales smartphone" if i % 4 == 0 else "fútbol",
                "hobbies_and_interests_list": '["tiktok"]' if i % 4 == 0 else "[]",
                "career_goals_and_ambitions": "",
                "backstory": f"Soy persona {i}.\n\nContexto profesional: Trabajo en sector {i}.",
                "digital_score": 0.5 if i % 4 == 0 else 0.1,
                "consumption_tags_json": "[]",
                "income_usd_monthly": 400.0 + i,
                "economic_role": "consumer",
                "adoption_propensity": 0.5,
            }
        )

    pl.DataFrame(rows).write_parquet(processed / "personas_enriched.parquet")
    meta = {
        "row_count": len(rows),
        "enriched_bytes": (processed / "personas_enriched.parquet").stat().st_size,
        "schema_version": "enriched_v1",
    }
    (processed / "build_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return root


@pytest.fixture
def generator(project_fixture):
    from salvador_personas.stage0.generator import PersonaGenerator

    return PersonaGenerator(str(project_fixture))
