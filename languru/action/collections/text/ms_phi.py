from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction


class MicrosoftPhi3Mini128kAction(TransformersAction):
    MODEL_NAME = (
        "microsoft/Phi-3-mini-128k-instruct"  # microsoft/Phi-3-mini-4k-instruct
    )

    def name(self) -> Text:
        return "microsoft_phi3_mini_128k_action"


class MicrosoftPhi3Mini4kAction(TransformersAction):
    MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"

    def name(self) -> Text:
        return "microsoft_phi3_mini_4k_action"


class MicrosoftPhi3Action(MicrosoftPhi3Mini128kAction):
    MODEL_NAME = "microsoft/Phi-3-mini-128k-instruct"

    def name(self) -> Text:
        return "microsoft_phi3_action"


if __name__ == "__main__":
    from rich import print

    print(f"Loading {MicrosoftPhi3Action.MODEL_NAME} ...")
    action = MicrosoftPhi3Action()
    print(f'Loaded Model "{MicrosoftPhi3Action.MODEL_NAME}" Health: {action.health()}')
    print()

    # Chat
    chat_interactive(
        action=action, model=MicrosoftPhi3Action.MODEL_NAME, max_tokens=800
    )
