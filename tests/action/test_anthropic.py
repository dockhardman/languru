from languru.action.anthropic import AnthropicAction

test_chat_model_name = "claude-3-haiku-20240307"


def test_anthropic_action_health():
    action = AnthropicAction()
    assert action.name() == "anthropic_action"
    assert action.health() is True


def test_anthropic_action_chat():
    action = AnthropicAction()
    chat_completion = action.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    )
    assert chat_completion.choices[0].message.content


# def test_anthropic_action_chat_stream():
#     action = AnthropicAction()
#     answer = ""
#     for chat_chunk in action.chat_stream(
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Hello!"},
#         ],
#         model=test_chat_model_name,
#     ):
#         if chat_chunk.choices[0].delta.content:
#             answer += chat_chunk.choices[0].delta.content
#     assert answer
