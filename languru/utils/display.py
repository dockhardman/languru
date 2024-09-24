from typing import Dict, List, Text

from rich.panel import Panel
from rich.style import Style
from rich.text import Text as RichText


def display_messages_with_panel(
    messages: List[Dict], title: Text = "Messages", *, print_panel: bool = True
) -> RichText:
    """
    Display messages in a rich panel format.

    Parameters
    ----------
    messages : List[Dict]
        A list of message dictionaries, each containing 'role' and 'content'.
    title : Text, optional
        The title of the panel (default is "Messages").
    print_panel : bool, optional
        If True, prints the panel to the console (default is True).

    Returns
    -------
    RichText
        A RichText object containing the formatted messages.
    """

    content = RichText("")
    for m in messages:
        if m["role"] == "system":
            content += RichText(m["role"], style=Style(color="blue", italic=True))
        elif m["role"] == "user":
            content += RichText(m["role"], style=Style(color="green", italic=True))
        elif m["role"] == "assistant":
            content += RichText(m["role"], style=Style(color="red", italic=True))
        else:
            content += RichText(m["role"], style=Style(color="white", italic=True))
        content += RichText(":\n" + m["content"] + "\n\n")
    if print_panel:
        print(Panel(content, title=title))
    return content
