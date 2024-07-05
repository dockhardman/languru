from typing import cast

from openai._streaming import Stream
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from languru.openai_plugins.clients.google import GoogleOpenAI
from languru.utils.openai_utils import ensure_chat_completion_message_params

test_chat_model_name = "models/gemini-1.5-flash"
test_emb_model_name = "models/text-embedding-004"


google_openai = GoogleOpenAI()


def test_google_openai_chat_completions_create():
    chat_res = google_openai.chat.completions.create(
        messages=ensure_chat_completion_message_params(
            [
                {"role": "system", "content": "Respond simple and concise."},
                {"role": "user", "content": "Why sky is blue"},
            ]
        ),
        model=test_chat_model_name,
        temperature=2.0,
    )
    chat_res = cast(ChatCompletion, chat_res)
    assert chat_res.choices and chat_res.choices[0].message


def test_google_openai_chat_completions_create_stream():
    chat_stream = google_openai.chat.completions.create(
        messages=ensure_chat_completion_message_params(
            [
                {"role": "system", "content": "Respond simple and concise."},
                {"role": "user", "content": "Say Hi!"},
            ]
        ),
        model=test_chat_model_name,
        temperature=0.0,
        stream=True,
    )
    chat_stream = cast(Stream[ChatCompletionChunk], chat_stream)
    for chunk in chat_stream:
        if chunk.choices[0].finish_reason == "stop":
            pass
        else:
            assert chunk.choices and chunk.choices[0].delta.content


def test_google_openai_models_retrieve():
    model = google_openai.models.retrieve(model=test_chat_model_name)
    assert model.id == test_chat_model_name


def test_google_openai_models_list():
    model = google_openai.models.list()
    assert len(model.data) > 0


def test_google_openai_embeddings_create():
    emb_res = google_openai.embeddings.create(
        input="Hello, my name is John.",
        model=test_emb_model_name,
    )
    assert emb_res.data and emb_res.data[0].embedding
