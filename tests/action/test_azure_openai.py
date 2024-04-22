from languru.action.openai import AzureOpenaiAction

test_chat_model_name = "gpt-3.5-turbo"
test_embedding_model_name = "text-embedding-ada-002"


def test_openai_action_health():
    action = AzureOpenaiAction()
    assert action.name() == "azure_openai_action"
    assert action.health() is True


def test_openai_action_chat():
    action = AzureOpenaiAction()
    chat_completion = action.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    )
    assert chat_completion.choices[0].message.content


def test_openai_action_chat_stream():
    action = AzureOpenaiAction()
    answer = ""
    for chat_chunk in action.chat_stream(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    ):
        if chat_chunk.id and chat_chunk.choices[0].delta.content:
            answer += chat_chunk.choices[0].delta.content
    assert answer


def test_openai_action_embeddings():
    action = AzureOpenaiAction()
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
