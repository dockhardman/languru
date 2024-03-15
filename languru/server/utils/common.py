import logging
from typing import TYPE_CHECKING, Any, Optional, Text, Type, TypeVar

from languru.config import logger as languru_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

T = TypeVar("T")

NOT_SET = object()


def get_value_from_app(
    app: "FastAPI",
    key: Text,
    value_typing: Optional[Type[T]] = None,
    default: Any = NOT_SET,
    logger: Optional[logging.Logger] = None,
) -> T:
    logger = logger or languru_logger
    out = default
    if hasattr(app.state, key):
        if value_typing is None:
            out = getattr(app.state, key)
        else:
            if isinstance(getattr(app.state, key, None), value_typing) is False:
                logger.warning(f"Key {key} not of type {value_typing} in app.state")
            out = getattr(app.state, key)
    elif key in app.extra:
        if value_typing is None:
            out = app.extra[key]
        else:
            if isinstance(app.extra[key], value_typing) is False:
                logger.warning(f"Key {key} not of type {value_typing} in app.extra")
            out = app.extra[key]
    if out is NOT_SET:
        raise ValueError(
            f"Key {key} not found or not of type {value_typing} "
            + "in app.state or app.extra"
        )
    return out
