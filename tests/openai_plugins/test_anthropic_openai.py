from typing import cast

from openai._streaming import Stream
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from languru.openai_plugins.clients.anthropic import AnthropicOpenAI
from languru.utils.prompt import ensure_chat_completion_message_params

test_chat_model_name = "claude-3-haiku-20240307"


claude_openai = AnthropicOpenAI()


def test_claude_openai_models_retrieve():
    model = claude_openai.models.retrieve(model=test_chat_model_name)
    assert model.id == test_chat_model_name


def test_claude_openai_models_list():
    model_res = claude_openai.models.list()
    assert len(model_res.data) > 0 and any(
        [m.id == test_chat_model_name for m in model_res.data]
    )


def test_claude_openai_chat_completions_create():
    chat_res = claude_openai.chat.completions.create(
        messages=ensure_chat_completion_message_params(
            [
                {"role": "system", "content": "Respond simple and concise."},
                {"role": "user", "content": "Say Hi!"},
            ]
        ),
        model=test_chat_model_name,
        temperature=2.0,
    )
    chat_res = cast(ChatCompletion, chat_res)
    assert chat_res.choices and chat_res.choices[0].message


# def test_claude_openai_chat_completions_create_stream():
#     chat_stream = claude_openai.chat.completions.create(
#         messages=ensure_chat_completion_message_params(
#             [
#                 {"role": "system", "content": "Respond simple and concise."},
#                 {"role": "user", "content": "Say Hi!"},
#             ]
#         ),
#         model=test_chat_model_name,
#         temperature=0.0,
#         stream=True,
#     )
#     chat_stream = cast(Stream[ChatCompletionChunk], chat_stream)
#     for chunk in chat_stream:
#         print(chunk)
#         if chunk.choices[0].finish_reason == "stop":
#             pass
#         else:
#             assert chunk.choices and chunk.choices[0].delta.content
