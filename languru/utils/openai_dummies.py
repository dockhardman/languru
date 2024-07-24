import time
from typing import Optional, Text

from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.run_status import RunStatus

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


def get_dummy_message(
    message_id: Optional[Text] = None,
    *,
    assistant_id: Optional[Text] = None,
    thread_id: Optional[Text] = None,
    run_id: Optional[Text] = None,
    text: Optional[Text] = None,
) -> "Message":
    return Message.model_validate(
        {
            "id": message_id or rand_openai_id("msg"),
            "assistant_id": assistant_id,
            "attachments": [],
            "completed_at": None,
            "content": [
                {
                    "text": {"annotations": [], "value": text or "What is 2 + 2?"},
                    "type": "text",
                }
            ],
            "created_at": int(time.time()),
            "incomplete_at": None,
            "incomplete_details": None,
            "metadata": {},
            "object": "thread.message",
            "role": "user",
            "run_id": run_id,
            "status": "incomplete",
            "thread_id": thread_id or rand_openai_id("thread"),
        }
    )


def get_dummy_message_answer(
    message_id: Optional[Text] = None,
    *,
    assistant_id: Optional[Text] = None,
    thread_id: Optional[Text] = None,
    run_id: Optional[Text] = None,
    text: Optional[Text] = None,
) -> "Message":
    return Message.model_validate(
        {
            "id": message_id or rand_openai_id("msg"),
            "assistant_id": assistant_id,
            "attachments": [],
            "completed_at": None,
            "content": [
                {
                    "text": {"annotations": [], "value": text or "2 + 2 equals 4."},
                    "type": "text",
                }
            ],
            "created_at": int(time.time()),
            "incomplete_at": None,
            "incomplete_details": None,
            "metadata": {},
            "object": "thread.message",
            "role": "assistant",
            "run_id": run_id,
            "status": "completed",
            "thread_id": thread_id or rand_openai_id("thread"),
        }
    )


def get_dummy_run(
    run_id: Optional[Text] = None,
    *,
    assistant_id: Text,
    thread_id: Optional[Text] = None,
    status: RunStatus = "queued",
) -> "Run":
    return Run.model_validate(
        {
            "id": run_id or rand_openai_id("run"),
            "assistant_id": assistant_id,
            "cancelled_at": None,
            "completed_at": None,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + 600,
            "failed_at": None,
            "incomplete_details": None,
            "instructions": (
                "You are a personal math tutor. "
                + "Respond briefly and concisely to the user's questions."
            ),
            "metadata": {},
            "model": "gpt-4o-mini",
            "object": "thread.run",
            "parallel_tool_calls": True,
            "required_action": None,
            "response_format": "auto",
            "started_at": int(time.time()),
            "status": status,
            "thread_id": thread_id or rand_openai_id("thread"),
            "tool_choice": "auto",
            "tools": [],
            "truncation_strategy": {"type": "auto", "last_messages": None},
            "usage": None,
            "temperature": 1.0,
            "top_p": 1.0,
            "tool_resources": {},
        }
    )
