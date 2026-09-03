"""Integration tests against the real app, with the real trained model.

These need `models/` to exist, which is what running the notebook writes. That
is deliberate: a suite that stubbed the model out would pass while the service
returned nonsense.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """A client whose lifespan has run, so the model is loaded."""
    with TestClient(app) as test_client:
        yield test_client


def valid_flat() -> dict:
    """A request body that should always work."""
    return {
        "location": "mumbai",
        "area_sqft": 1000.0,
        "furnishing": "Semi-Furnished",
        "transaction": "Resale",
        "bathroom": 2,
        "balcony": 1,
        "floor_num": 5,
        "total_floors": 12,
    }


def test_health_reports_a_loaded_model(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["sklearn_version"]


def test_happy_path_returns_a_plausible_price(client):
    response = client.post("/predict", json=valid_flat())
    assert response.status_code == 200
    body = response.json()

    price = body["predicted_price"]
    assert price > 0
    # A 1000 sqft flat in Mumbai is between 10 Lac and 100 Cr. Wide on purpose:
    # this asserts the units are rupees, not that the model is good.
    assert 1e6 < price < 1e10, f"{price} is not in a sane rupee range"
    assert body["currency"] == "INR"
    assert body["location_known"] is True
    assert any(suffix in body["predicted_price_formatted"] for suffix in ("Lac", "Cr"))


def test_a_body_missing_a_required_field_is_rejected_with_422(client):
    body = valid_flat()
    del body["area_sqft"]
    response = client.post("/predict", json=body)
    assert response.status_code == 422
    assert "area_sqft" in response.text


def test_a_nonsense_area_is_rejected_with_422(client):
    body = valid_flat() | {"area_sqft": -50}
    assert client.post("/predict", json=body).status_code == 422


def test_a_flat_above_the_top_floor_is_rejected_with_422(client):
    body = valid_flat() | {"floor_num": 40, "total_floors": 10}
    response = client.post("/predict", json=body)
    assert response.status_code == 422
    assert "total_floors" in response.text


def test_an_unseen_city_is_answered_and_flagged(client):
    body = valid_flat() | {"location": "atlantis"}
    response = client.post("/predict", json=body)
    assert response.status_code == 200, "an unknown city must not be an error"
    assert response.json()["location_known"] is False, "but the caller must be told"
    assert response.json()["predicted_price"] > 0


def test_a_bigger_flat_in_the_same_city_predicts_more(client):
    small = client.post("/predict", json=valid_flat() | {"area_sqft": 600}).json()
    large = client.post("/predict", json=valid_flat() | {"area_sqft": 2400}).json()
    assert large["predicted_price"] > small["predicted_price"]


def test_locations_lists_only_cities_the_model_knows(client):
    response = client.get("/locations")
    assert response.status_code == 200
    cities = response.json()
    assert cities and "mumbai" in cities
