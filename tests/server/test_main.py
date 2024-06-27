import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


def test_app_health(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
