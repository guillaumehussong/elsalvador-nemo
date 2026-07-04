from fastapi.testclient import TestClient
import pytest

from salvador_personas.api.app import app


def test_health():
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_estimate_focus():
    client = TestClient(app)
    r = client.post(
        "/api/focus/estimate",
        json={
            "stimulus": "Abonnement 10 USD/mes pour streaming local.",
            "n": 4,
            "seed": 42,
            "departments": ["San Salvador"],
        },
    )
    if r.status_code == 503:
        pytest.skip("cache personas absent")
    assert r.status_code == 200
    data = r.json()
    assert data["n"] == 4
    assert "estimated_cost_usd" in data
    assert data["estimated_cost_usd"] > 0
