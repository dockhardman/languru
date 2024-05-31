from typing import Text

from pyassorted.string.rand import rand_str


def rand_chat_completion_id() -> Text:
    return f"chatcmpl-{rand_str(29)}"
