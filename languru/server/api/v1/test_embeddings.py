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
def mocked_openai_embeddings_create():
    from openai.resources.embeddings import Embeddings as OpenaiEmbeddings

    from languru.examples.return_values._openai import return_embedding

    with patch.object(
        OpenaiEmbeddings,
        "create",
        MagicMock(return_value=return_embedding),
    ):
        yield


@pytest.fixture
def mocked_model_discovery_list():
    from languru.resources.model.discovery import ModelDiscovery, SqlModelDiscovery
    from languru.types.model import Model

    return_model_discovery_list = [
        Model(
            id="gpt-3.5-turbo",
            created=int(time.time()) - 1,
            object="model",
            owned_by="http://0.0.0.0:8682/v1",
        )
    ]
    with patch.object(
        ModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ), patch.object(
        SqlModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ):
        yield


def test_llm_app_embedding(llm_env):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        embedding_call = {
            "input": ["Hello", "world!"],
            "model": "text-embedding-ada-002",
            "encoding_format": "float",
        }
        response = client.post("/v1/embeddings", json=embedding_call)
        assert response.status_code == 200
        assert len(response.json()["data"]) == len(embedding_call["input"])


def test_agent_app_embedding(
    agent_env, mocked_model_discovery_list, mocked_openai_embeddings_create
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        embedding_call = {
            "input": ["Hello", "world!"],
            "model": "text-embedding-ada-002",
            "encoding_format": "float",
        }
        response = client.post("/v1/embeddings", json=embedding_call)
        assert response.status_code == 200
