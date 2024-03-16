import importlib
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import languru.server.main
from languru.server.config import AppType

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def llm_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.llm)


@pytest.fixture
def agent_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.agent)


@pytest.fixture
def mocked_model_discovery_list():
    from languru.examples.return_values._openai import return_model
    from languru.resources.model.discovery import ModelDiscovery, SqlModelDiscovery

    with patch.object(
        ModelDiscovery, "list", MagicMock(return_value=[return_model])
    ), patch.object(SqlModelDiscovery, "list", MagicMock(return_value=[return_model])):
        yield


@pytest.fixture
def mocked_model_discovery_retrieve():
    from languru.examples.return_values._openai import return_model
    from languru.resources.model.discovery import ModelDiscovery, SqlModelDiscovery

    with patch.object(
        ModelDiscovery, "retrieve", MagicMock(return_value=return_model)
    ), patch.object(
        SqlModelDiscovery, "retrieve", MagicMock(return_value=return_model)
    ):
        yield


def test_llm_app_models(llm_env):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert len(data["data"]) > 0


def test_llm_app_model_retrieve(llm_env):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        response = client.get("/v1/models/gpt-3.5-turbo")
        assert response.status_code == 200

        response = client.get("/v1/models/MODEL_NOT_FOUND")
        assert response.status_code == 404


def test_llm_app_model_register(llm_env):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        model = {
            "id": "model_id",
            "created": int(time.time()),
            "object": "model",
            "owned_by": "pytest",
        }
        response = client.post("/v1/models/register", json=model)
        assert response.status_code == 403


def test_agent_app_models(agent_env, mocked_model_discovery_list):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert len(data["data"]) > 0


def test_agent_app_model_retrieve(agent_env, mocked_model_discovery_retrieve):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        response = client.get("/v1/models/model_id")
        assert response.status_code == 200


def test_agent_app_model_register(agent_env):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        model = {
            "id": "test_model_id",
            "created": int(time.time()),
            "object": "model",
            "owned_by": "pytest",
        }
        response = client.post("/v1/models/register", json=model)
        assert response.status_code == 200
