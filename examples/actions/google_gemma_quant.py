from typing import Text
import time
from rich import print

from languru.action.hf import TransformersAction


class GoogleGemmaChatAction(TransformersAction):
    # Model configuration
    MODEL_NAME = "google/gemma-7b-it"

    # Model Quantization configuration
    use_quantization = True

    def name(self) -> Text:
        return "google_gemma_chat_action"


def chat(**kwargs):
    action = GoogleGemmaChatAction(**kwargs)
    print(f"Health: {action.health()}")

    start = time.time()
    chat_params = {
        "model": action.MODEL_NAME,
        "messages": [
            {"role": "user", "content": "What is the capital of the United States?"},
        ],
        "max_tokens": 200,
    }
    chat_res = action.chat(**chat_params)
    timecost = time.time() - start
    if chat_res.usage:
        print(
            f"Tokens Rate: {chat_res.usage.completion_tokens / timecost:.2f} "
            + f"tokens/s, in config: {kwargs}"
        )


if __name__ == "__main__":
    chat(load_in_8bit=True)
    chat(load_in_4bit=True)
