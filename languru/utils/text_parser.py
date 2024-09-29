import hashlib
import re
import string
import unicodedata
from typing import List, Optional, Sequence, Text

full_width_punctuation = "".join(
    chr(ord(ch) + 0xFEE0) if ch in string.punctuation else ch
    for ch in string.punctuation
)
strip_punctuation = string.punctuation + full_width_punctuation + " "


def hash_text(text: Text) -> Text:
    """Hash a string using SHA-256."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def full_to_half(text: Text) -> Text:
    """Convert full-width characters to half-width.

    Parameters
    ----------
    text : Text
        The input string containing full-width characters.

    Returns
    -------
    Text
        A string with all full-width characters converted to half-width.
    """

    return unicodedata.normalize("NFKC", text)


def split_strip(
    content: Text,
    separators: Sequence[Text] = (",", "、", "，", "/", "\\", "|", "“", "\n", " or "),
) -> List[Text]:
    """Split a string by specified separators and strip punctuation.

    Parameters
    ----------
    content : Text
        The input string to be split and stripped.
    separators : Sequence[Text], optional
        A sequence of strings used as separators (default is
        (",", "、", "，", "/", "\\", "|", "“", "\n")).

    Returns
    -------
    List[Text]
        A list of stripped strings obtained by splitting the input content.
    """

    # Escape special regex characters and join separators
    pattern = "|".join(map(re.escape, separators))
    # Split the text using the pattern
    splitted_contents = re.split(pattern, content)

    return [s.strip(strip_punctuation) for s in splitted_contents]


def search_line_in_content(
    content: Text,
    *,
    prefix: Optional[Text] = None,
) -> Optional[Text]:

    for line in content.splitlines():
        line = line.strip(" -_*")
        if prefix:
            if line.startswith(prefix):
                return "".join(line.split(prefix)[1:]).strip()
    return None
