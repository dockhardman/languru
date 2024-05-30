from typing import Any, Dict, List, Sequence, Text

from openai.types.chat import ChatCompletionMessageParam


def ensure_chat_completion_message_params(
    messages: (
        Sequence[ChatCompletionMessageParam]
        | Sequence[Dict[Text, Any]]
        | ChatCompletionMessageParam
        | Dict[Text, Any]
    )
) -> List[ChatCompletionMessageParam]:
    """Ensure the messages parameter is a list of ChatCompletionMessageParam objects."""

    if not messages:
        raise ValueError("The messages parameter is required.")

    return list([messages] if isinstance(messages, Dict) else messages)  # type: ignore
