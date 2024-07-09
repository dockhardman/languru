import time
from typing import Text

import pytest
from openai.types.beta.assistant import Assistant

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.utils.openai_utils import rand_assistant_id


def test_openai_backend(session_id_fixture: Text):
    openai_backend = OpenaiBackend(url="sqlite:///:memory:")
    openai_backend.touch()

    # Create assistants
    assistant_id = rand_assistant_id()
    assistant = openai_backend.assistants.create(
        Assistant.model_validate(
            {
                "id": assistant_id,
                "created_at": int(time.time()),
                "description": "Math Tutor",
                "instructions": "You are a personal math tutor. Write and run code to answer math questions.",  # noqa: E501
                "metadata": {},
                "model": "models/gemini-1.5-flash",
                "name": "Math Tutor",
                "object": "assistant",
                "tools": [],
                "temperature": 0.7,
            }
        )
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
