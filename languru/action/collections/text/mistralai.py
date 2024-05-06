from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction


class Mistral7bInstructAction(TransformersAction):
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

    def name(self) -> Text:
        return "mistralai_7b_instruct_action"


class Mistral8x7bInstructAction(TransformersAction):
    MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def name(self) -> Text:
        return "mistralai_8x7b_instruct_action"


class Mistral8x22bInstructAction(TransformersAction):
    MODEL_NAME = "mistralai/Mixtral-8x22B-Instruct-v0.1"

    def name(self) -> Text:
        return "mistralai_8x22b_instruct_action"


if __name__ == "__main__":
    from rich import print

    print(f"Loading {Mistral7bInstructAction.MODEL_NAME} ...")
    action = Mistral7bInstructAction()
    print(
        f'Loaded Model "{Mistral7bInstructAction.MODEL_NAME}" '
        + f"Health: {action.health()}"
    )
    print()

    # Chat
    chat_interactive(
        action=action, model=Mistral7bInstructAction.MODEL_NAME, max_tokens=800
    )
