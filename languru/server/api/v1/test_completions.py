import importlib
import json
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
def mocked_openai_text_completion_create():
    from openai.resources.completions import Completions as OpenaiCompletions

    from languru.examples.return_values._openai import return_text_completion

    with patch.object(
        OpenaiCompletions,
        "create",
        MagicMock(return_value=return_text_completion),
    ):
        yield


@pytest.fixture
def mocked_openai_text_completion_create_stream():
    from openai.resources.completions import Completions as OpenaiCompletions

    from languru.examples.return_values._openai import return_text_completion_stream

    with patch.object(
        OpenaiCompletions,
        "create",
        MagicMock(return_value=return_text_completion_stream),
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


def test_llm_app_text_completions(llm_env, mocked_openai_text_completion_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        completion_call = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
        }
        response = client.post("/v1/completions", json=completion_call)
        assert response.status_code == 200
        assert response.json()["choices"][0]["text"]


def test_llm_app_text_completions_stream(
    llm_env, mocked_openai_text_completion_create_stream
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        completion_call = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
            "stream": True,
        }
        with client.stream(
            "POST", url="/v1/completions", json=completion_call
        ) as response:
            answer = ""
            for line in response.iter_lines():
                line = line.replace("data:", "", 1).strip()
                if line and line != "[DONE]":
                    chat_chunk = json.loads(line)
                    if chat_chunk["choices"][0]["text"]:
                        answer += chat_chunk["choices"][0]["text"]
            assert answer


def test_agent_app_chat(
    agent_env, mocked_model_discovery_list, mocked_openai_text_completion_create
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        completion_call = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
        }
        response = client.post("/v1/completions", json=completion_call)
        assert response.status_code == 200


def test_agent_app_chat_stream(
    agent_env, mocked_model_discovery_list, mocked_openai_text_completion_create_stream
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        completion_call = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
            "stream": True,
        }
        with client.stream(
            "POST", url="/v1/completions", json=completion_call
        ) as response:
            answer = ""
            for line in response.iter_lines():
                line = line.replace("data:", "", 1).strip()
                if line and line != "[DONE]":
                    chat_chunk = json.loads(line)
                    if chat_chunk["choices"][0]["text"]:
                        answer += chat_chunk["choices"][0]["text"]
            assert answer
