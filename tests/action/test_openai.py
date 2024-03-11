from languru.action.openai import OpenaiAction

test_chat_model_name = "gpt-3.5-turbo"
test_text_completion_model_name = "gpt-3.5-turbo-instruct"
test_embedding_model_name = "text-embedding-3-small"
test_moderation_model_name = "text-moderation-latest"


def test_openai_action_health():
    action = OpenaiAction()
    assert action.name() == "openai_action"
    assert action.health() is True


def test_openai_action_chat():
    action = OpenaiAction()
    chat_completion = action.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    )
    assert chat_completion.choices[0].message.content


def test_openai_action_chat_stream():
    action = OpenaiAction()
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


def test_openai_action_text_completion():
    action = OpenaiAction()
    text_completion = action.text_completion(
        prompt="The reverse of a dog is a",
        model=test_text_completion_model_name,
        max_tokens=20,
    )
    assert text_completion.choices[0].text


def test_openai_action_text_completion_stream():
    action = OpenaiAction()
    answer = ""
    for text_chunk in action.text_completion_stream(
        prompt="The reverse of a dog is a",
        model=test_text_completion_model_name,
        max_tokens=20,
    ):
        if text_chunk.choices[0].text:
            answer += text_chunk.choices[0].text
    assert answer


def test_openai_action_embeddings():
    action = OpenaiAction()
    embedding = action.embeddings(
        input=[
            "Discover your spirit of adventure and indulge your thirst for "
            + "wanderlust with the touring bike that has dominated the segment "
            + "for the past 50 years: the Honda Gold Wing Tour, Gold Wing Tour "
            + "Automatic DCT, and Gold Wing Tour Airbag Automatic DCT.",
            "R1M: This is the most advanced production motorcycle for riders "
            + "who are at the very top of their game.",
        ],
        model=test_embedding_model_name,
    )
    assert len(embedding.data[0].embedding) == 1536


def test_openai_action_moderation():
    action = OpenaiAction()
    moderation = action.moderations(
        input="I am a helpful assistant.",
        model=test_moderation_model_name,
    )
    for res in moderation.results:
        assert res.categories.harassment is False
        assert res.categories.hate is False
        assert res.categories.self_harm is False
        assert res.categories.sexual is False
        assert res.categories.violence is False
        assert res.flagged is False
        assert res.category_scores.harassment < 0.001
        assert res.category_scores.hate < 0.001
        assert res.category_scores.self_harm < 0.001
