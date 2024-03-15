from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from languru.server.config import AppType

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def llm_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.llm)


@pytest.fixture
def agent_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.agent)


def test_llm_app_health(llm_env):
    from languru.server.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_agent_app_health(agent_env):
    from languru.server.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
