import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Text, Type, TypeVar, Union

from languru.config import logger as languru_logger

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.openapi.models import Example

T = TypeVar("T")

NOT_SET = object()


def get_value_from_app(
    app: "FastAPI",
    key: Text,
    value_typing: Optional[Type[T]] = None,
    default: Any = NOT_SET,
    logger: Optional[logging.Logger] = None,
) -> T:
    """Get value from app.state or app.extra.

    Parameters
    ----------
    app : FastAPI
        The FastAPI app instance.
    key : Text
        The key to get from app.state or app.extra.
    value_typing : Optional[Type[T]], optional
        The type to check the value against, by default None.
    default : Any, optional
        The default value to return if key is not found, by default NOT_SET.
    logger : Optional[logging.Logger], optional
        The logger to use, by default None.

    Returns
    -------
    T
        The value from app.state or app.extra.

    Raises
    ------
    ValueError
        If key is not found in app.state or app.extra.
    """

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
                logger.warning(f"Key '{key}' not of type {value_typing} in app.extra")
            out = app.extra[key]
    if out is NOT_SET:
        raise ValueError(
            f"Key {key} not found or not of type {value_typing} "
            + "in app.state or app.extra"
        )
    return out


def to_openapi_examples(
    openapi_examples: Union[Dict[Text, "Example"], Dict]
) -> Dict[Text, "Example"]:
    return openapi_examples
