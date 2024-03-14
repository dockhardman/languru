from typing import TYPE_CHECKING, Any, Optional, Text, Type, TypeVar

if TYPE_CHECKING:
    from fastapi import FastAPI

T = TypeVar("T")

NOT_SET = object()


def get_value_from_app(
    app: "FastAPI",
    key: Text,
    value_type: Optional[Type[T]] = None,
    default: Any = NOT_SET,
) -> T:
    out = default
    if hasattr(app.state, key):
        if value_type is None:
            out = getattr(app.state, key)
        else:
            if isinstance(getattr(app.state, key, None), value_type):
                out = getattr(app.state, key)
    elif key in app.extra:
        if value_type is None:
            out = app.extra[key]
        elif isinstance(app.extra[key], value_type):
            out = app.extra[key]
    if out is NOT_SET:
        raise ValueError(
            f"Key {key} not found or not of type {value_type} in app.state or app.extra"
        )
    return out
