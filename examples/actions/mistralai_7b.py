import time

from rich import print

from languru.action.hf import TransformersAction
from languru.types.chat.completions import ChatCompletionRequest, Message


class Mistral7BAction(TransformersAction):
    # Model configuration
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"


chat_params = ChatCompletionRequest.model_validate(
    {
        "model": Mistral7BAction.MODEL_NAME,
        "messages": [
            # Not allowed system role
            # Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is your favorite condiment?"),
            Message(
                role="assistant",
                content=(
                    "Well, I'm quite partial to a good squeeze of fresh lemon juice. "
                    + "It adds just the right amount of zesty flavour to whatever "
                    + "I'm cooking up in the kitchen!"
                ),
            ),
            Message(role="user", content="Do you have mayonnaise recipes?"),
        ],
        "max_tokens": 800,
    }
)
action = Mistral7BAction()

start = time.time()
res = action.chat(**chat_params.model_dump(exclude_none=True))
for c in res.choices:
    print(f"{c.message.role}: {c.message.content}")
timecost = time.time() - start
print(f"Timecost: {timecost:.02f} s")
if res.usage:
    print(f"Tokens Rate: {res.usage.completion_tokens / timecost:.02f} tokens/s")
