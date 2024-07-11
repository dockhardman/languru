from pprint import pformat
from typing import Text

import pytest
from openai.types.beta.assistant import Assistant

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.utils.openai_dummies import (
    get_dummy_assistant,
    get_dummy_message,
    get_dummy_thread,
)
from languru.utils.openai_utils import rand_openai_id


def test_openai_backend_assistants_apis(session_id_fixture: Text):
    openai_backend = OpenaiBackend(url="sqlite:///:memory:")
    openai_backend.touch()

    # Create assistants
    assistant_id = rand_openai_id("asst")
    assistant = openai_backend.assistants.create(
        Assistant.model_validate(get_dummy_assistant(assistant_id))
    )
    assert assistant.id == assistant_id

    # Get assistants
    assistants = openai_backend.assistants.list()
    assert len(assistants) == 1
    assistant_retrieved = openai_backend.assistants.retrieve(assistant_id)
    assert assistant_retrieved.id == assistant_id

    # Update assistant
    update_description = "Math Tutor for kids"
    assistant_updated = openai_backend.assistants.update(
        assistant_id, description=update_description
    )
    assert assistant_updated.description == update_description
    assistant_retrieved = openai_backend.assistants.retrieve(assistant_id)
    assert assistant_retrieved.id == assistant_id
    assert assistant_retrieved.description == update_description

    # Delete assistant
    delete_result = openai_backend.assistants.delete(assistant_id)
    assert delete_result.id == assistant_id
    assistants = openai_backend.assistants.list()
    assert len(assistants) == 0
    with pytest.raises(NotFound):
        openai_backend.assistants.retrieve(assistant_id)


def test_openai_backend_threads_apis(session_id_fixture: Text):
    openai_backend = OpenaiBackend(url="sqlite:///:memory:")
    openai_backend.touch()

    # Create thread
    thread_id = rand_openai_id("thread")
    thread = openai_backend.threads.create(get_dummy_thread(thread_id))
    assert thread.id == thread_id

    # Get thread
    thread_retrieved = openai_backend.threads.retrieve(thread_id)
    assert thread_retrieved.id == thread_id

    # Update thread
    update_metadata = {"key": "value"}
    thread_updated = openai_backend.threads.update(thread_id, metadata=update_metadata)
    assert pformat(thread_updated.metadata) == pformat(update_metadata)

    # Delete thread
    delete_result = openai_backend.threads.delete(thread_id)
    assert delete_result.id == thread_id
    with pytest.raises(NotFound):
        openai_backend.threads.retrieve(thread_id)


def test_openai_backend_threads_messages_apis(session_id_fixture: Text):
    openai_backend = OpenaiBackend(url="sqlite:///:memory:")
    openai_backend.touch()

    # Create thread
    thread_id = rand_openai_id("thread")
    thread = openai_backend.threads.create(get_dummy_thread(thread_id))
    assert thread.id == thread_id

    # Create message
    message_id = rand_openai_id("message")
    message = openai_backend.threads.messages.create(
        get_dummy_message(message_id, thread_id=thread_id)
    )
    assert message.id == message_id

    # Get message
    message_retrieved = openai_backend.threads.messages.retrieve(
        message_id, thread_id=thread_id
    )
    assert message_retrieved.id == message_id

    # Update message
    update_metadata = {"key": "value"}
    message_updated = openai_backend.threads.messages.update(
        message_id, thread_id=thread_id, metadata=update_metadata
    )
    assert pformat(message_updated.metadata) == pformat(update_metadata)

    # Delete message
    delete_result = openai_backend.threads.messages.delete(
        message_id, thread_id=thread_id
    )
    assert delete_result.id == message_id
    with pytest.raises(NotFound):
        openai_backend.threads.messages.retrieve(message_id, thread_id=thread_id)
