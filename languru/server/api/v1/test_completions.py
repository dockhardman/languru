import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

test_model_name = "gpt-3.5-turbo-instruct"


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


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


def test_app_text_completions(test_client, mocked_openai_text_completion_create):
    completion_call = {
        "model": test_model_name,
        "prompt": "Say this is a test",
        "max_tokens": 7,
        "temperature": 0,
    }
    response = test_client.post("/v1/completions", json=completion_call)
    assert response.status_code == 200
    assert response.json()["choices"][0]["text"]


def test_app_text_completions_stream(
    test_client, mocked_openai_text_completion_create_stream
):
    completion_call = {
        "model": test_model_name,
        "prompt": "Say this is a test",
        "max_tokens": 7,
        "temperature": 0,
        "stream": True,
    }
    with test_client.stream(
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
