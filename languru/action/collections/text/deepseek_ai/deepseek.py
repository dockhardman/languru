from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction


class DeepSeekV2Chat(TransformersAction):
    MODEL_NAME = "deepseek-ai/DeepSeek-V2-Chat"

    def name(self) -> Text:
        return "deepseek_v2_chat"


class DeepSeekChat(DeepSeekV2Chat):
    def name(self) -> Text:
        return "deepseek_chat"


if __name__ == "__main__":
    from rich import print

    action_class = DeepSeekChat

    print(f"Loading {action_class.MODEL_NAME} ...")
    action = action_class()
    print(f'Loaded Model "{action_class.MODEL_NAME}" ' + f"Health: {action.health()}")
    print()

    # Chat
    chat_interactive(action=action, model=action_class.MODEL_NAME, max_tokens=800)
