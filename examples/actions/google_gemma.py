from typing import Text

from rich import print

from languru.action.hf import TransformersAction


class GoogleGemmaChatAction(TransformersAction):
    # Model configuration
    MODEL_NAME = "google/gemma-2b-it"
    # google/gemma-7b-it, google/gemma-7b, google/gemma-2b-it, google/gemma-2b

    def name(self) -> Text:
        return "google_gemma_chat_action"


class GoogleGemmaAction(TransformersAction):
    # Model configuration
    MODEL_NAME = "google/gemma-2b"
    # google/gemma-7b-it, google/gemma-7b, google/gemma-2b-it, google/gemma-2b

    def name(self) -> Text:
        return "google_gemma_action"


def chat():
    action = GoogleGemmaChatAction()
    print(f"Health: {action.health()}")

    chat_params = {
        "model": "google/gemma-2b-it",
        "messages": [
            {"role": "user", "content": "What is the capital of the United States?"},
        ],
        "max_tokens": 200,
    }
    chat_res = action.chat(**chat_params)
    print(chat_res)


def text_generation():
    action = GoogleGemmaAction()
    print(f"Health: {action.health()}")

    text_completion = action.text_completion(
        model="google/gemma-2b",
        prompt="Write me a poem about Machine Learning.",
        max_tokens=200,
    )
    print(text_completion)


if __name__ == "__main__":
    chat()
    # text_generation()
