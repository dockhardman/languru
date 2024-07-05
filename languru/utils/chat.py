import copy
from typing import Dict, List, Optional, Text, Union

from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pyassorted.string import Bracket, multiple_replace

from languru.types.chat.completions import Message
from languru.utils.common import display_messages
from languru.utils.openai_utils import (
    ensure_chat_completion_message_params,
    ensure_openai_chat_completion_content,
)


def chat_completion_once(
    *,
    # Message input
    messages: Optional[Union[List[Dict], List["Message"]]] = None,
    query: Optional[Text] = None,
    system: Optional[Text] = None,
    # OpenAI client
    client: OpenAI,
    model: Text,
    prompt_vars: Optional[Dict] = None,
    verbose: bool = False,
    temperature: float = 0.3,
    wrapped_by: Bracket = Bracket.CurlyBrackets,
    **kwargs,
) -> Text:
    """Chat once with the OpenAI client."""

    messages_input: List[ChatCompletionMessageParam] = []
    if messages:
        messages_input.extend(
            ensure_chat_completion_message_params(
                [
                    m.model_dump() if isinstance(m, Message) else copy.deepcopy(m)
                    for m in messages
                ]
            )
        )
    elif query:
        if system:
            messages_input.append(
                ChatCompletionSystemMessageParam(role="system", content=system)
            )
        messages_input.append(
            ChatCompletionUserMessageParam(role="user", content=query)
        )
    else:
        raise ValueError("Either 'messages' or 'query' must be provided")
    for m in messages_input:
        _content = m.get("content")
        if isinstance(_content, Text):
            m["content"] = multiple_replace(
                prompt_vars or {}, _content, wrapped_by=wrapped_by
            ).strip()

    if verbose:
        display_messages(
            messages=messages_input,
            table_title=f"{client.__class__.__name__} Chat Messages Input",
        )
    chat_res: "ChatCompletion" = client.chat.completions.create(
        messages=messages_input,
        model=model,
        temperature=temperature,
        stream=False,
    )  # type: ignore
    chat_answer = ensure_openai_chat_completion_content(chat_res)
    if verbose:
        display_messages(
            messages=[{"role": "assistant", "content": chat_answer}],
            table_title=f"{client.__class__.__name__}({model}) Chat Response",
        )

    return chat_answer
