import time
from typing import Text

import torch
from rich import print

from languru.action.hf import TransformersAction

run_times = 3


class GoogleGemmaChatAction(TransformersAction):
    # Model configuration
    MODEL_NAME = "google/gemma-7b-it"

    # Model Quantization configuration
    use_quantization = True

    def name(self) -> Text:
        return "google_gemma_chat_action"


def chat(**kwargs):
    action = GoogleGemmaChatAction(**kwargs)
    assert action.health() is True

    # Init model
    chat_params = {
        "model": action.MODEL_NAME,
        "messages": [
            {"role": "user", "content": "What is the capital of the United States?"},
        ],
        "max_tokens": 200,
    }
    chat_res = action.chat(**chat_params)

    start = time.time()
    total_completion_tokens = 0
    for _ in range(run_times):
        chat_res = action.chat(**chat_params)
        if chat_res.usage:
            total_completion_tokens += chat_res.usage.completion_tokens
    timecost = time.time() - start
    print(
        f"Tokens Rate: {total_completion_tokens / timecost:.2f} "
        + f"tokens/s, in config: {kwargs}"
    )
    # GPU ram usage
    if torch.cuda.is_available():
        allocated_bytes = torch.cuda.memory_allocated("cuda:0")
        total_bytes = torch.cuda.get_device_properties("cuda:0").total_memory
        allocated_gb = allocated_bytes / 1024**3
        total_gb = total_bytes / 1024**3
        memory_usage_str = f"{allocated_gb:.2f}/{total_gb:.2f} GB"
        print(f"GPU memory usage: {memory_usage_str}")


if __name__ == "__main__":
    chat(use_quantization=False)
    chat(load_in_8bit=True)
    chat(load_in_4bit=True)
    chat(use_flash_attention=True)
