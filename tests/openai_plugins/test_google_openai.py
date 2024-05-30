from typing import cast

from openai.types.chat.chat_completion import ChatCompletion

from languru.openai_plugins.clients.google import GoogleOpenAI
from languru.utils.prompt import ensure_chat_completion_message_params

test_model_name = "models/gemini-1.5-flash"


google_openai = GoogleOpenAI()


def test_google_openai_chat_completion_create():
    chat_res = google_openai.chat.completions.create(
        messages=ensure_chat_completion_message_params(
            [
                {"role": "system", "content": "Respond simple and concise."},
                {"role": "user", "content": "Why sky is blue"},
            ]
        ),
        model=test_model_name,
        temperature=2.0,
    )
    chat_res = cast(ChatCompletion, chat_res)
    assert chat_res.choices and chat_res.choices[0].message
