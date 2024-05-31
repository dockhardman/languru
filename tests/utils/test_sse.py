from typing import Any, Text

import pytest
from pydantic import BaseModel

from languru.utils.sse import simple_encode_sse


class MyBaseModel(BaseModel):
    name: Text


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"Hello", b"data: Hello\n\n"),
        ("Hello", b"data: Hello\n\n"),
        ({"hello": "world"}, b'data: {"hello": "world"}\n\n'),
        ([1, 2, 3], b"data: [1, 2, 3]\n\n"),
        (MyBaseModel(name="Hello"), b'data: {"name": "Hello"}\n\n'),
    ],
)
def test_simple_encode_sse(data: Any, expected: bytes):
    assert simple_encode_sse(data) == expected
