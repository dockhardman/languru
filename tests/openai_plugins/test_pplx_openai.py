from languru.openai_plugins.clients.pplx import PerplexityOpenAI
from languru.utils.prompt import ensure_chat_completion_message_params

test_chat_model_name = "llama-3-8b-instruct"


pplx_openai = PerplexityOpenAI()


def test_pplx_openai_chat_completions_create():
    chat_res = pplx_openai.chat.completions.create(
        messages=ensure_chat_completion_message_params(
            [
                {"role": "system", "content": "Respond simple and concise."},
                {"role": "user", "content": "Say Hi!"},
            ]
        ),
        model=test_chat_model_name,
        temperature=1.99,
    )
    assert chat_res.choices and chat_res.choices[0].message


def test_pplx_openai_chat_completions_create_stream():
    chat_stream = pplx_openai.chat.completions.create(
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
    for chunk in chat_stream:
        if chunk.choices[0].finish_reason == "stop":
            pass
        else:
            assert chunk.choices and chunk.choices[0].delta.content


def test_pplx_openai_models_retrieve():
    model = pplx_openai.models.retrieve(model=test_chat_model_name)
    assert model.id == test_chat_model_name


def test_pplx_openai_models_list():
    model_res = pplx_openai.models.list()
    assert len(model_res.data) > 0 and any(
        [m.id == test_chat_model_name for m in model_res.data]
    )
