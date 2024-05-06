from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction


class GoogleGemma7bChatAction(TransformersAction):
    MODEL_NAME = "google/gemma-7b-it"

    def name(self) -> Text:
        return "google_gemma_7b_chat_action"


class GoogleGemma2bChatAction(TransformersAction):
    MODEL_NAME = "google/gemma-2b-it"

    def name(self) -> Text:
        return "google_gemma_2b_chat_action"


class GoogleGemma7b4bitChatAction(TransformersAction):
    MODEL_NAME = "google/gemma-7b-it"

    use_quantization = True
    load_in_4bit = True

    def name(self) -> Text:
        return "google_gemma_7b_4bit_chat_action"


class GoogleGemma2b4bitChatAction(TransformersAction):
    MODEL_NAME = "google/gemma-2b-it"

    use_quantization = True
    load_in_4bit = True

    def name(self) -> Text:
        return "google_gemma_2b_4bit_chat_action"


class GoogleGemmaChatAction(GoogleGemma7bChatAction):

    def name(self) -> Text:
        return "google_gemma_chat_action"


if __name__ == "__main__":
    from rich import print

    print(f"Loading {GoogleGemmaChatAction.MODEL_NAME} ...")
    action = GoogleGemmaChatAction()
    print(
        f'Loaded Model "{GoogleGemmaChatAction.MODEL_NAME}" Health: {action.health()}'
    )
    print()

    # Chat
    chat_interactive(
        action=action, model=GoogleGemmaChatAction.MODEL_NAME, max_tokens=800
    )
