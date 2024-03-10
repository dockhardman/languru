from languru.action.groq import GroqAction, GroqOpenaiAction


def test_groq_action():
    action = GroqAction()
    assert action.name() == "groq_action"
    assert action.health() is True

    # Test chat
    user_say = "Explain the importance of low latency LLMs in one short sentence"
    chat_completion = action.chat(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    )
    assert chat_completion.choices[0].message.content

    # Test chat stream
    answer = ""
    for _chat in action.chat_stream(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    ):
        if _chat.choices[0].delta.content:
            answer += _chat.choices[0].delta.content
    assert answer


def test_groq_openai_action():
    action = GroqOpenaiAction()
    assert action.name() == "groq_openai_action"
    assert action.health() is True

    # Test chat
    user_say = "Explain the importance of low latency LLMs in one short sentence"
    chat_completion = action.chat(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    )
    assert chat_completion.choices[0].message.content

    # Test chat stream
    answer = ""
    for _chat in action.chat_stream(
        messages=[{"role": "user", "content": user_say}], model="mixtral-8x7b-32768"
    ):
        if _chat.choices[0].delta.content:
            answer += _chat.choices[0].delta.content
    assert answer