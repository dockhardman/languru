from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction

MODEL_NAME = "google/gemma-7b-it"  # "google/gemma-2b-it"


class GoogleGemmaChatAction(TransformersAction):
    MODEL_NAME = MODEL_NAME

    def name(self) -> Text:
        return "google_gemma_chat_action"


if __name__ == "__main__":
    from rich import print

    print(f"Loading {MODEL_NAME} ...")
    action = GoogleGemmaChatAction()
    print(f'Loaded model "{MODEL_NAME}" Health: {action.health()}')
    print()

    # Chat
    chat_interactive(action=action, model=MODEL_NAME, max_tokens=800)
