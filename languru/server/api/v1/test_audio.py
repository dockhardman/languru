import importlib
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from openai._legacy_response import HttpxBinaryResponseContent
from openai.resources.audio.speech import Speech
from openai.resources.audio.transcriptions import Transcriptions
from openai.resources.audio.translations import Translations
from openai.types.audio import Transcription, Translation

import languru.server.main
from languru.server.config import AppType
from languru.types.audio import (
    AudioSpeechRequest,
    AudioTranscriptionRequest,
    AudioTranslationRequest,
)

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def llm_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.llm)


@pytest.fixture
def agent_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.agent)


@pytest.fixture
def mocked_openai_speech_response_create():
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
def mocked_openai_audio_transcriptions_create():
    with patch.object(
        Transcriptions,
        "create",
        MagicMock(return_value=Transcription(text="Transcribed text")),
    ):
        yield


@pytest.fixture
def mocked_openai_audio_translations_create():
    with patch.object(
        Translations,
        "create",
        MagicMock(return_value=Translation(text="Translated text")),
    ):
        yield


@pytest.fixture
def mocked_model_discovery_list():
    from languru.resources.model_discovery.base import DiskCacheModelDiscovery as MD
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
    with patch.object(MD, "list", MagicMock(return_value=return_model_discovery_list)):
        yield


def test_llm_app_audio_speech(llm_env, mocked_openai_speech_response_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = AudioSpeechRequest.model_validate(
            {"input": "Hello!", "model": "tts-1", "voice": "alloy"}
        )
        response = client.post(
            "/v1/audio/speech", json=request_call.model_dump(exclude_none=True)
        )
        assert response.status_code == 200


def test_llm_app_audio_transcriptions(
    llm_env, mocked_openai_audio_transcriptions_create
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = AudioTranscriptionRequest.model_validate(
            {
                "file": ("audio.mp3", b"This is a test audio content", "audio/mpeg"),
                "model": "whisper-1",
            }
        )
        response = client.post(
            "/v1/audio/transcriptions", files=request_call.to_files_form()
        )
        assert response.status_code == 200


def test_llm_app_audio_translations(llm_env, mocked_openai_audio_translations_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = AudioTranslationRequest.model_validate(
            {
                "file": ("audio.mp3", b"This is a test audio content", "audio/mpeg"),
                "model": "whisper-1",
            }
        )
        response = client.post(
            "/v1/audio/translations", files=request_call.to_files_form()
        )
        assert response.status_code == 200


def test_agent_app_audio_speech(
    agent_env, mocked_openai_speech_response_create, mocked_model_discovery_list
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = AudioSpeechRequest.model_validate(
            {"input": "Hello!", "model": "tts-1", "voice": "alloy"}
        )
        response = client.post(
            "/v1/audio/speech", json=request_call.model_dump(exclude_none=True)
        )
        assert response.status_code == 200
        print(response.text)


def test_agent_app_audio_transcriptions(
    agent_env, mocked_openai_audio_transcriptions_create, mocked_model_discovery_list
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = AudioTranscriptionRequest.model_validate(
            {
                "file": ("audio.mp3", b"This is a test audio content", "audio/mpeg"),
                "model": "whisper-1",
            }
        )
        response = client.post(
            "/v1/audio/transcriptions", files=request_call.to_files_form()
        )
        assert response.status_code == 200


def test_agent_app_audio_translations(
    agent_env, mocked_openai_audio_translations_create, mocked_model_discovery_list
):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = AudioTranslationRequest.model_validate(
            {
                "file": ("audio.mp3", b"This is a test audio content", "audio/mpeg"),
                "model": "whisper-1",
            }
        )
        response = client.post(
            "/v1/audio/translations", files=request_call.to_files_form()
        )
        assert response.status_code == 200
