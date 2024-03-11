from languru.action.pplx import PerplexityAction

test_chat_model_name = "sonar-small-chat"


def test_perplexity_action_health():
    action = PerplexityAction()
    assert action.name() == "perplexity_action"
    assert action.health() is True


def test_perplexity_action_chat():
    action = PerplexityAction()
    chat_completion = action.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    )
    assert chat_completion.choices[0].message.content


def test_perplexity_action_chat_stream():
    action = PerplexityAction()
    answer = ""
    for chat_chunk in action.chat_stream(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    ):
        if chat_chunk.choices[0].delta.content:
            answer += chat_chunk.choices[0].delta.content
    assert answer
