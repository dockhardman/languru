import json
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


def test_llm_app_chat(llm_env):
    from languru.server.main import app

    with TestClient(app) as client:

        chat_call = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        }
        response = client.post("/v1/chat/completions", json=chat_call)
        assert response.status_code == 200


def test_llm_app_chat_stream(llm_env):
    from languru.server.main import app

    with TestClient(app) as client:

        chat_call = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            "stream": True,
        }
        with client.stream(
            "POST", url="/v1/chat/completions", json=chat_call
        ) as response:
            answer = ""
            for line in response.iter_lines():
                line = line.replace("data:", "", 1).strip()
                if line and line != "[DONE]":
                    chat_chunk = json.loads(line)
                    if chat_chunk["choices"][0]["delta"]["content"]:
                        answer += chat_chunk["choices"][0]["delta"]["content"]
            assert answer
