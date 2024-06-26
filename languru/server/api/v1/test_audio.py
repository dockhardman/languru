from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from openai._legacy_response import HttpxBinaryResponseContent
from openai.resources.audio.speech import Speech
from openai.resources.audio.transcriptions import Transcriptions
from openai.resources.audio.translations import Translations
from openai.types.audio import Transcription, Translation

from languru.types.audio import (
    AudioSpeechRequest,
    AudioTranscriptionRequest,
    AudioTranslationRequest,
)


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


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


def test_app_audio_speech(test_client, mocked_openai_speech_response_create):
    request_call = AudioSpeechRequest.model_validate(
        {"input": "Hello!", "model": "tts-1", "voice": "alloy"}
    )
    response = test_client.post(
        "/v1/audio/speech", json=request_call.model_dump(exclude_none=True)
    )
    assert response.status_code == 200


def test_app_audio_transcriptions(
    test_client, mocked_openai_audio_transcriptions_create
):
    request_call = AudioTranscriptionRequest.model_validate(
        {
            "file": ("audio.mp3", b"This is a test audio content", "audio/mpeg"),
            "model": "whisper-1",
        }
    )
    response = test_client.post(
        "/v1/audio/transcriptions", files=request_call.to_files_form()
    )
    assert response.status_code == 200


def test_app_audio_translations(test_client, mocked_openai_audio_translations_create):
    request_call = AudioTranslationRequest.model_validate(
        {
            "file": ("audio.mp3", b"This is a test audio content", "audio/mpeg"),
            "model": "whisper-1",
        }
    )
    response = test_client.post(
        "/v1/audio/translations", files=request_call.to_files_form()
    )
    assert response.status_code == 200
