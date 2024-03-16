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
    from languru.resources.model.discovery import ModelDiscovery, SqlModelDiscovery
    from languru.types.model import Model

    return_model_discovery_list = [
        Model(
            id="text-moderation-latest",
            created=int(time.time()) - 1,
            object="model",
            owned_by="pytest",
        )
    ]
    with patch.object(
        ModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ), patch.object(
        SqlModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ):
        yield


@pytest.fixture
def mocked_openai_moderation_create():
    from openai.resources.moderations import Moderations

    from languru.examples.return_values._openai import return_moderation_create

    with patch.object(
        Moderations, "create", MagicMock(return_value=return_moderation_create)
    ), patch.object(
        Moderations, "create", MagicMock(return_value=return_moderation_create)
    ):
        yield


def test_llm_app_moderation(llm_env):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        moderation_call = {"input": "I want to kill them."}
        response = client.post("/v1/moderations", json=moderation_call)
        assert response.status_code == 200


def test_agent_app_moderation(
    agent_env, mocked_model_discovery_list, mocked_openai_moderation_create
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        moderation_call = {"input": "I want to kill them."}
        response = client.post("/v1/moderations", json=moderation_call)
        assert response.status_code == 200
