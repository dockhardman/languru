from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction


class StableMLChat(TransformersAction):
    MODEL_NAME = "stabilityai/stablelm-2-12b-chat"

    def name(self) -> Text:
        return "stableml_chat"


if __name__ == "__main__":
    from rich import print

    action_class = StableMLChat

    print(f"Loading {action_class.MODEL_NAME} ...")
    action = action_class()
    print(f'Loaded Model "{action_class.MODEL_NAME}" ' + f"Health: {action.health()}")
    print()

    # Chat
    chat_interactive(action=action, model=action_class.MODEL_NAME, max_tokens=800)
