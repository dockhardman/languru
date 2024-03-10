from languru.action.groq import GroqAction, GroqOpenaiAction

user_say = "Explain the importance of low latency LLMs in one short sentence"


def test_groq_action_health():
    action = GroqAction()
    assert action.name() == "groq_action"
    assert action.health() is True


def test_groq_action_chat():
    action = GroqAction()
    chat_completion = action.chat(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    )
    assert chat_completion.choices[0].message.content


def test_groq_action_chat_stream():
    action = GroqAction()
    answer = ""
    for _chat in action.chat_stream(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    ):
        if _chat.choices[0].delta.content:
            answer += _chat.choices[0].delta.content
    assert answer


def test_groq_openai_action_health():
    action = GroqOpenaiAction()
    assert action.name() == "groq_openai_action"
    assert action.health() is True


def test_groq_openai_action_chat():
    action = GroqAction()
    chat_completion = action.chat(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    )
    assert chat_completion.choices[0].message.content


def test_groq_openai_action_chat_stream():
    action = GroqAction()
    answer = ""
    for _chat in action.chat_stream(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    ):
        if _chat.choices[0].delta.content:
            answer += _chat.choices[0].delta.content
    assert answer
