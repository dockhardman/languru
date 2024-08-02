import pytest
from fastapi.testclient import TestClient
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.thread_deleted import ThreadDeleted

from languru.types.openai_assistants import AssistantCreateRequest
from languru.types.openai_threads import ThreadCreateRequest
from tests.conftest import *  # noqa: F401, F403


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


def test_threads_apis(test_client):
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

    # Retrieve the thread
    res = test_client.get(f"/v1/threads/{thread.id}")
    res.raise_for_status()
    retrieved_thread = Thread.model_validate(res.json())
    assert retrieved_thread.id == thread.id

    # List threads
    res = test_client.get("/v1/threads")
    res.raise_for_status()
    retrieved_threads = [Thread.model_validate(thread) for thread in res.json()["data"]]
    assert len(retrieved_threads) == 1
    assert retrieved_threads[0].id == thread.id

    # Update the thread
    res = test_client.post(
        f"/v1/threads/{thread.id}", json={"metadata": {"my_key": "my_value"}}
    )
    res.raise_for_status()
    retrieved_thread = Thread.model_validate(res.json())
    assert retrieved_thread.id == thread.id
    assert (
        retrieved_thread.metadata
        and retrieved_thread.metadata.get("my_key") == "my_value"  # type: ignore
    )

    # Delete the thread
    res = test_client.delete(f"/v1/threads/{thread.id}")
    res.raise_for_status()
    deleted_thread = ThreadDeleted.model_validate(res.json())
    assert deleted_thread.id == thread.id
    assert deleted_thread.deleted is True
    res = test_client.get(f"/v1/threads/{thread.id}")
    assert res.status_code == 404


def test_threads_runs_apis(test_client):
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
