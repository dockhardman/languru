import importlib
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response

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
def mocked_openai_speech_stream_response_create():
    from openai._legacy_response import HttpxBinaryResponseContent
    from openai.resources.audio.speech import Speech

    httpx_res = Response(200)
    httpx_res._content = b"bytes chunks"
    httpx_binary_res_content = HttpxBinaryResponseContent(httpx_res)

    with patch.object(
        Speech,
        "create",
        MagicMock(return_value=httpx_binary_res_content),
    ):
        yield


@pytest.fixture
def mocked_model_discovery_list():
    from languru.resources.model.discovery import ModelDiscovery, SqlModelDiscovery
    from languru.types.model import Model

    return_model_discovery_list = [
        Model(
            id="tts-1",
            created=int(time.time()) - 1,
            object="model",
            owned_by="http://0.0.0.0:8682/v1",
        ),
        Model(
            id="whisper-1",
            created=int(time.time()) - 1,
            object="model",
            owned_by="http://0.0.0.0:8682/v1",
        ),
    ]
    with patch.object(
        ModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ), patch.object(
        SqlModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ):
        yield


def test_llm_app_audio_speech(llm_env, mocked_openai_speech_stream_response_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        chat_call = {"input": "Hello!", "model": "tts-1", "voice": "alloy"}
        response = client.post("/v1/audio/speech", json=chat_call)
        assert response.status_code == 200
