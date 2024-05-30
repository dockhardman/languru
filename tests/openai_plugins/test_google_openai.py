from languru.openai_plugins.clients.google import GoogleOpenAI
from languru.utils.prompt import ensure_chat_completion_message_params

test_model_name = "models/gemini-1.5-flash"


google_openai = GoogleOpenAI()


def test_google_openai_chat_completion_create():
    res = google_openai.chat.completions.create(
        messages=ensure_chat_completion_message_params(
            [{"role": "user", "content": "Why sky is blue"}]
        ),
        model=test_model_name,
    )
    print(res)
    assert True
