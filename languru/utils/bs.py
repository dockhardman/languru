from typing import Text

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


def bs4_to_str(element: Tag | NavigableString | None) -> Text:
    if isinstance(element, NavigableString):
        return str(element).strip()
    elif isinstance(element, Tag):
        return element.get_text(strip=True)
    else:
        return ""


def drop_no_used_attrs(html_content: Text | BeautifulSoup) -> Text:
    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
    for tag in soup.find_all():
        if "jsname" in tag.attrs:
            del tag["jsname"]
        if "data-ved" in tag.attrs:
            del tag["data-ved"]
        if "data-csiid" in tag.attrs:
            del tag["data-csiid"]
        if "data-atf" in tag.attrs:
            del tag["data-atf"]
        if "ping" in tag.attrs:
            del tag["ping"]
        if "src" in tag.attrs:
            del tag["src"]
        if "jsaction" in tag.attrs:
            del tag["jsaction"]
        if "jscontroller" in tag.attrs:
            del tag["jscontroller"]
        if "style" in tag.attrs:
            del tag["style"]

        if "class" in tag.attrs:
            filtered_classes = [
                cls for cls in tag["class"] if not (len(cls) == 6 and cls.isalnum())
            ]
            if filtered_classes:
                tag["class"] = filtered_classes
            else:
                del tag["class"]

    return str(soup)


def drop_all_styles(html_content: Text | BeautifulSoup) -> Text:
    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
    for tag in soup.find_all():
        # Check if the tag has a 'style' attribute
        if "style" in tag.attrs:
            # Remove the 'style' attribute
            del tag["style"]
    return str(soup)
