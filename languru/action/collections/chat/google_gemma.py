from typing import Dict, List, Text

from languru.action.hf import TransformersAction

MODEL_NAME = "google/gemma-7b-it"  # "google/gemma-2b-it"


class GoogleGemmaChatAction(TransformersAction):
    MODEL_NAME = MODEL_NAME

    def name(self) -> Text:
        return "google_gemma_chat_action"


if __name__ == "__main__":
    import time

    from rich.console import Console
    from rich.prompt import Prompt

    console = Console()

    console.print(f"Loading {MODEL_NAME} ...")
    action = GoogleGemmaChatAction()
    console.print(f'Loaded model "{MODEL_NAME}" Health: {action.health()}')
    console.print()

    # Chat
    messages: List[Dict] = []
    while True:
        user_says = Prompt.ask("User", console=console).strip()
        if user_says:
            if user_says.casefold() in ("exit", "quit", "q"):
                break

            messages.append({"role": "user", "content": user_says})
            chat_params = {
                "model": "gemma-7b-it",
                "messages": messages,
                "max_tokens": 200,
            }
            chat_start = time.time()
            chat_res = action.chat(**chat_params)
            chat_timecost = time.time() - chat_start
            assert len(chat_res.choices) > 0 and chat_res.choices[0].message.content
            assistant_says = chat_res.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_says})
            console.print(f"Assistant: {assistant_says}")
            # Tokens per second
            res_total_tokens = (
                0.0 if chat_res.usage is None else chat_res.usage.total_tokens
            )
            console.print(
                f"{res_total_tokens / chat_timecost:.3f} tokens/s", style="italic blue"
            )
