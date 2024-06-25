import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


def test_app_models(test_client):
    response = test_client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) > 0


def test_app_model_retrieve(test_client):
    response = test_client.get("/v1/models/gpt-3.5-turbo")
    assert response.status_code == 200

    response = test_client.get("/v1/models/MODEL_NOT_FOUND")
    assert response.status_code == 404
