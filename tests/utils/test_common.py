import pytest

from languru.utils.common import display_messages, remove_punctuation


def test_remove_punctuation():
    assert remove_punctuation("Hello, World!") == "Hello World"
    assert remove_punctuation("Hello, World！") == "Hello World"
    assert remove_punctuation("Hello, World❤️", extra_punctuation="❤️") == "Hello World"


@pytest.mark.parametrize(
    "input_messages",
    [
        ([{"role": "user", "content": "Hello, world!"}],),
        ([{"role": "bot", "content": "Hi there!"}],),
        ([{"role": "assistant", "content": "How can I assist?"}],),
        ([{"role": None, "content": None}],),
        ([],),  # Empty list case
    ],
)
def test_display_messages(input_messages):
    if input_messages:
        assert display_messages(input_messages)
    else:
        with pytest.raises(ValueError):
            display_messages(input_messages)
