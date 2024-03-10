from languru.action.hf import TransformersAction

test_model_name = "sshleifer/tiny-gpt2"
test_embedding_model_name = "sentence-transformers-testing/stsb-bert-tiny-safetensors"


def test_transformers_action_health():
    action = TransformersAction.from_models(model=test_model_name)
    assert action.name() == "transformers_action"
    assert action.health() is True


def test_transformers_action_chat():
    action = TransformersAction.from_models(model=test_model_name)
    chat_completion = action.chat(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        model=test_model_name,
        max_tokens=50,
    )
    assert chat_completion.choices[0].message.content


def test_transformers_action_text_completion():
    action = TransformersAction.from_models(model=test_model_name)
    text_completion = action.text_completion(
        prompt="The reverse of a dog is a", model=test_model_name, max_tokens=50
    )
    print(text_completion.choices[0].text)
    assert text_completion.choices[0].text


def test_transformers_action_embeddings():
    action = TransformersAction.from_models(model=test_embedding_model_name)
    embedding = action.embeddings(
        input=[
            "Discover your spirit of adventure and indulge your thirst for "
            + "wanderlust with the touring bike that has dominated the segment "
            + "for the past 50 years: the Honda Gold Wing Tour, Gold Wing Tour "
            + "Automatic DCT, and Gold Wing Tour Airbag Automatic DCT.",
            "R1M: This is the most advanced production motorcycle for riders "
            + "who are at the very top of their game.",
        ],
        model=test_model_name,
    )
    assert len(embedding.data[0].embedding) == 128
