import pytest
from fastapi.testclient import TestClient
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread

from languru.types.openai_assistants import AssistantCreateRequest
from languru.types.openai_threads import ThreadCreateRequest
from tests.conftest import *  # noqa: F401, F403


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


def test_threads_apis(test_client):
    # Create an assistant
    res = test_client.post(
        "/v1/assistants",
        json=AssistantCreateRequest.model_validate(
            {
                "model": "gpt-4o-mini",
                "description": (
                    "You are a personal math tutor. "
                    + "Respond briefly and concisely to the user's questions."
                ),
                "name": "Math Tutor",
            }
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    assistant = Assistant.model_validate(res.json())

    # Create a thread
    res = test_client.post(
        "/v1/threads",
        json=ThreadCreateRequest.model_validate(
            {
                "messages": [
                    {
                        "content": "Hello, I need help with a math problem.",
                        "role": "user",
                    },
                    {"content": "Sure, what is the problem?", "role": "assistant"},
                ]
            }
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    thread = Thread.model_validate(res.json())
