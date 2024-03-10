from languru.action.google import GoogleGenaiAction

test_model_name = "gemini-pro"
test_embedding_model_name = "embedding-001"


def test_google_genai_action_health():
    action = GoogleGenaiAction()
    assert action.name() == "google_genai_action"
    assert action.health() is True


def test_google_genai_action_chat():
    action = GoogleGenaiAction()
    chat_completion = action.chat(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        model=test_model_name,
    )
    assert chat_completion.choices[0].message.content


def test_google_genai_action_text_completion():
    action = GoogleGenaiAction()
    text_completion = action.text_completion(
        prompt="The reverse of a dog is a", model=test_model_name, max_tokens=20
    )
    assert text_completion.choices[0].text


def test_google_genai_action_embeddings():
    action = GoogleGenaiAction()
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
    assert len(embedding.data[0].embedding) == 768
