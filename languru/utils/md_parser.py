import re
from typing import Optional, Text


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


def clean_markdown_links(markdown_text):
    """Remove Markdown link syntax from the given text.

    Parameters
    ----------
    markdown_text : str
        The input string containing Markdown links.

    Returns
    -------
    str
        The cleaned string with Markdown links removed.
    """

    # Remove Markdown link syntax
    cleaned_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", markdown_text)
    return cleaned_text
