from typing import Any, List, Optional, Text, Tuple, TypeVar

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


def must_list_or_none(value: List[T] | Any) -> Optional[List[T]]:
    if isinstance(value, List):
        if len(value) == 0:
            return None
        return value
    elif isinstance(value, Tuple):
        if len(value) == 0:
            return None
        return list(value)
    elif value is None:
        return None
    else:
        return [value]


def must_list(value: List[T] | Any) -> List[T]:
    if must_list_or_none(value) is None:
        raise ValueError(f"Could not convert {value} to a list")
    return value
