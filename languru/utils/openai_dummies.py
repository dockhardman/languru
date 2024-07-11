import time
from typing import Optional, Text

from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread

from languru.utils.openai_utils import rand_openai_id


def get_dummy_assistant(assistant_id: Optional[Text] = None) -> "Assistant":
    return Assistant.model_validate(
        {
            "id": assistant_id or rand_openai_id("asst"),
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


def get_dummy_thread(thread_id: Optional[Text] = None) -> "Thread":
    return Thread.model_validate(
        {
            "id": thread_id or rand_openai_id("thread"),
            "created_at": int(time.time()),
            "metadata": {},
            "object": "thread",
            "tool_resources": {},
        }
    )
