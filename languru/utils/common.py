import json
import string
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Text,
    Tuple,
    TypeVar,
    Union,
)

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from rich import box
from rich import print as rich_print
from rich.style import StyleType
from rich.table import Table
from rich.text import Text as RichText

from languru.config import console, logger
from languru.types.chat.completions import Message

if TYPE_CHECKING:
    from openai.types.chat.chat_completion import ChatCompletion

T = TypeVar("T")


def should_str_or_none(value: Text | Any) -> Optional[Text]:
    if isinstance(value, Text):
        return value
    elif value is None:
        return None
    logger.warning(f"Value {value} is not a string, returning None")
    return None


def should_str(value: Text | Any) -> Text:
    if should_str_or_none(value) is None:
        raise ValueError(f"Value {value} is not a string")
    return value


def must_list_or_none(
    value: List[T] | Any, return_none_if_empty: bool = False
) -> Optional[List[T]]:
    if isinstance(value, List):
        if return_none_if_empty and len(value) == 0:
            return None
        return value
    elif isinstance(value, Tuple):
        if return_none_if_empty and len(value) == 0:
            return None
        return list(value)
    elif value is None:
        return None
    else:
        return [value]


def must_list(value: List[T] | Any) -> List[T]:
    to_items = must_list_or_none(value)
    if to_items is None:
        raise ValueError(f"Could not convert {value} to a list")
    return to_items


def debug_print(
    *values: Any,
    title: Text = "Debug Print",
    box: box.Box | None = box.HEAVY_HEAD,
    colors: List[StyleType] = [
        "bright_blue",
        "bright_cyan",
        "bright_green",
        "bright_magenta",
    ],
) -> None:
    if not values:
        return
    tb = Table(title=RichText(title), box=box, show_header=False)
    for idx, value in enumerate(values):
        style = colors[idx % len(colors)]
        if isinstance(value, BaseModel):
            tb.add_row(value.model_dump_json(indent=2), style=style)
        elif isinstance(value, dict):
            tb.add_row(json.dumps(value, indent=2, ensure_ascii=False), style=style)
        else:
            tb.add_row(str(value), style=style)
    rich_print(tb)


def replace_right(source_str: Text, old: Text, new: Text, occurrence: int = -1) -> Text:
    return source_str[::-1].replace(old[::-1], new[::-1], occurrence)[::-1]


def str_strong_casefold(text: Text) -> Text:
    return text.strip().replace("-_. ", "").casefold()


def remove_punctuation(input_string: Text, extra_punctuation: Text = "") -> Text:
    """Remove punctuations from the input string."""

    extended_punctuation = (
        string.punctuation + "，？！（）【】《》“”‘’；：" + extra_punctuation
    )
    translator = str.maketrans("", "", extended_punctuation)
    return input_string.translate(translator)


def ensure_openai_chat_completion_content(chat_completion: "ChatCompletion") -> Text:
    """Ensure that the chat completion response content is returned."""

    chat_answer = chat_completion.choices[0].message.content
    if chat_answer is None:
        raise ValueError("Failed to get a response content from the OpenAI API.")
    return chat_answer


def ensure_list(value: Any) -> List:
    if isinstance(value, Sequence):
        return list(value)
    if value is None:
        return []
    return [value]


def ensure_openai_chat_completion_message_params(
    messages: Union[
        Sequence["Message"],
        Sequence[Dict[Text, Any]],
        Sequence[ChatCompletionMessageParam],
    ]
) -> List[ChatCompletionMessageParam]:
    """Ensure that the chat completion messages are in the correct format."""

    _messages: List[ChatCompletionMessageParam] = []
    for m in messages:
        if isinstance(m, Message):
            m_dict = m.model_dump()
            if m_dict.get("role") not in ["user", "assistant", "system"]:
                raise ValueError(f"Invalid role: {m_dict.get('role')}")
            _messages.append(m_dict)  # type: ignore
        elif isinstance(m, Dict):
            if m.get("role") not in ["user", "assistant", "system"]:
                raise ValueError(f"Invalid role: {m.get('role')}")
            _messages.append(m)  # type: ignore
        elif isinstance(m, ChatCompletionMessageParam.__args__):
            _messages.append(m)
        else:
            raise ValueError(f"Invalid message type: {m}")
    return _messages


def display_messages(
    messages: Union[
        Sequence["Message"],
        Sequence[Dict[Text, Any]],
        Sequence[ChatCompletionMessageParam],
    ],
    is_print: bool = True,
) -> Text:
    """Display messages in a human-readable format."""

    if not messages:
        raise ValueError("No messages to display.")

    _messages = [
        m.model_dump() if isinstance(m, BaseModel) else dict(m) for m in messages
    ]
    out = ""
    for m in _messages:
        role = str(m.get("role") or "Unknown").capitalize()
        content = str(m.get("content") or "n/a")
        if is_print:
            console.print(role, style="underline bold cyan")
            console.print(content)
            console.print()
        out += f"\n\n{role.capitalize()}:\n{content}"
        out = out.strip()
    return out


def named_tuples_to_dicts(named_tuples: Sequence[NamedTuple]) -> List[Dict]:
    """Convert named tuples to dictionaries."""

    return [nt._asdict() for nt in named_tuples]


def json_dumps(data: Any, indent: Optional[Union[int, Text]] = None) -> Text:
    return json.dumps(data, indent=indent, ensure_ascii=False)
