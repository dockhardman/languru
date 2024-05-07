from typing import Text

from languru.action.base import chat_interactive
from languru.action.hf import TransformersAction


class NvidiaLlama3ChatQA8B(TransformersAction):
    MODEL_NAME = "nvidia/Llama3-ChatQA-1.5-8B"

    def name(self) -> Text:
        return "nvidia_llama3_chatqa_8b"


class NvidiaLlama3ChatQA(NvidiaLlama3ChatQA8B):
    def name(self) -> Text:
        return "nvidia_llama3_chatqa"


if __name__ == "__main__":
    from rich import print

    action_class = NvidiaLlama3ChatQA

    print(f"Loading {action_class.MODEL_NAME} ...")
    action = action_class()
    print(f'Loaded Model "{action_class.MODEL_NAME}" ' + f"Health: {action.health()}")
    print()

    # Chat
    chat_interactive(action=action, model=action_class.MODEL_NAME, max_tokens=800)
