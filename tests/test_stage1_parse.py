import pytest

from salvador_personas.stage1.parse import extract_json_object


def test_extract_json_from_markdown_fence():
    raw = '```json\n{"sentiment": "positivo", "interest_score": 8, "objections": [], "verbatim": "Dale."}\n```'
    data = extract_json_object(raw)
    assert data["interest_score"] == 8
