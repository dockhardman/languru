import re
import string
import unicodedata
from typing import List, Optional, Sequence, Text

full_width_punctuation = "".join(
    chr(ord(ch) + 0xFEE0) if ch in string.punctuation else ch
    for ch in string.punctuation
)
strip_punctuation = string.punctuation + full_width_punctuation + " "


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
    separators: Sequence[Text] = (",", "、", "，", "/", "\\", "|", "“", "\n"),
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
    splitted_content = re.split(pattern, content)
    return [s.strip(strip_punctuation) for s in splitted_content]


def extract_markdown_section_content(markdown: Text, section: Text) -> Optional[Text]:
    """Extract content from a specific section of a markdown string.

    Parameters
    ----------
    markdown : Text
        The input markdown string.
    section : Text
        The section header to search for.

    Returns
    -------
    Optional[Text]
        The content of the specified section if found, otherwise None.
    """

    pattern = rf"#+\s.*?{section}:?(.*?)(?=## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None
