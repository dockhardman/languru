import json

import pytest
from fastapi.testclient import TestClient
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.thread_deleted import ThreadDeleted
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.message_deleted import MessageDeleted
from openai.types.beta.threads.run import Run

from languru.types.openai_assistants import AssistantCreateRequest
from languru.types.openai_threads import (
    ThreadCreateRequest,
    ThreadsMessageUpdate,
    ThreadsRunCreate,
    ThreadUpdateRequest,
)
from tests.conftest import *  # noqa: F401, F403

test_assistant_create_request = json.dumps(
    {
        "name": "Math Tutor",
        "instructions": (
            "You are a personal math tutor. "
            + "Respond briefly and concisely to the user's questions."
        ),
        "model": "gpt-4o-mini",
    }
)
test_messages_begin = json.dumps(
    [
        {"content": "Hello, I need help with a math problem.", "role": "user"},
        {"content": "Sure, what is the problem?", "role": "assistant"},
    ]
)
test_user_query = json.dumps({"content": "What is 2 + 2?", "role": "user"})


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
            {"messages": json.loads(test_messages_begin)}
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
        f"/v1/threads/{thread.id}",
        json=ThreadUpdateRequest.model_validate(
            {"metadata": {"my_key": "my_value"}}
        ).model_dump(exclude_none=True),
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


def test_threads_messages_apis(test_client):
    # Create a thread
    res = test_client.post(
        "/v1/threads",
        json=ThreadCreateRequest.model_validate(
            {"messages": json.loads(test_messages_begin)}
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    thread = Thread.model_validate(res.json())

    # Retrieve the messages
    res = test_client.get(f"/v1/threads/{thread.id}/messages")
    res.raise_for_status()
    messages_begin = [Message.model_validate(item) for item in res.json()["data"]]
    assert len(messages_begin) == len(json.loads(test_messages_begin))
    for m in messages_begin:
        res = test_client.get(f"/v1/threads/{thread.id}/messages/{m.id}")
        res.raise_for_status()
        Message.model_validate(res.json())

    # Add a message
    res = test_client.post(
        f"/v1/threads/{thread.id}/messages", json=json.loads(test_user_query)
    )
    res.raise_for_status()
    message_created = Message.model_validate(res.json())
    assert (
        Message.model_validate(
            test_client.get(
                f"/v1/threads/{thread.id}/messages/{message_created.id}"
            ).json()
        ).id
        == message_created.id
    )
    assert len(test_client.get(f"/v1/threads/{thread.id}/messages").json()["data"]) == 3

    # Update the message
    res = test_client.post(
        f"/v1/threads/{thread.id}/messages/{message_created.id}",
        json=ThreadsMessageUpdate.model_validate(
            {"metadata": {"my_key": "my_value"}}
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    message_updated = Message.model_validate(res.json())
    assert message_updated.id == message_created.id
    assert (
        message_updated.metadata
        and message_updated.metadata.get("my_key") == "my_value"  # type: ignore
    )

    # Delete the message
    res = test_client.delete(f"/v1/threads/{thread.id}/messages/{message_created.id}")
    res.raise_for_status()
    deleted_message = MessageDeleted.model_validate(res.json())
    assert deleted_message.id == message_created.id
    assert deleted_message.deleted is True
    assert (
        test_client.get(
            f"/v1/threads/{thread.id}/messages/{message_created.id}"
        ).status_code
        == 404
    )
    assert len(test_client.get(f"/v1/threads/{thread.id}/messages").json()["data"]) == 2


def test_threads_runs_apis(test_client):
    # Create an assistant
    res = test_client.post(
        "/v1/assistants",
        json=AssistantCreateRequest.model_validate(
            json.loads(test_assistant_create_request)
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    assistant = Assistant.model_validate(res.json())

    # Create a thread
    res = test_client.post(
        "/v1/threads",
        json=ThreadCreateRequest.model_validate(
            {"messages": json.loads(test_messages_begin)}
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    thread = Thread.model_validate(res.json())

    # Create user message
    res = test_client.post(
        f"/v1/threads/{thread.id}/messages", json=json.loads(test_user_query)
    )
    res.raise_for_status()
    assert Message.model_validate(res.json())

    # Create a run
    res = test_client.post(
        f"/v1/threads/{thread.id}/runs",
        json=ThreadsRunCreate.model_validate(
            {
                "assistant_id": assistant.id,
                "thread_id": thread.id,
                "additional_instructions": "Your name is John.",
                "additional_messages": [
                    {
                        "role": "assistant",
                        "content": (
                            "<thinking>The question is simple, "
                            + "I can answer directly.</thinking>"
                        ),
                    }
                ],
                "temperature": 0.0,
            }
        ).model_dump(exclude_none=True),
    )
    res.raise_for_status()
    run = Run.model_validate(res.json())
