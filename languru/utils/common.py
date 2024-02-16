import json
from typing import Any, List, Optional, Text, Tuple, TypeVar

from pydantic import BaseModel
from rich import box
from rich import print as rich_print
from rich.style import StyleType
from rich.table import Table
from rich.text import Text as RichText

from languru.config import logger

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
