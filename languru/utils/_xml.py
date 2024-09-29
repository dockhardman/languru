import re
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from typing import Dict, List, Text


def remove_xml_declaration(xml_string):
    """Remove the XML declaration from a given XML string.

    Parameters
    ----------
    xml_string : str
        The XML string from which the declaration should be removed.

    Returns
    -------
    str
        The XML string without the XML declaration.
    """

    return re.sub(r"<\?xml[^>]+\?>\s*", "", xml_string, count=1)


def to_xml(chat_list: List[Dict] | Dict) -> "ET.Element":
    """Convert a list of chat entries or a single chat entry to an XML Element.

    Parameters
    ----------
    chat_list : List[Dict] or Dict
        A list of dictionaries representing chat entries or a single dictionary.

    Returns
    -------
    ET.Element
        An XML Element representing the chat records.
    """

    chat_list = chat_list if isinstance(chat_list, List) else [chat_list]

    root = ET.Element("chat_record")
    for entry in chat_list:
        role = entry["role"]
        content = entry["content"]
        child = ET.SubElement(root, role)
        child.text = content
    return root


def pretty_xml(_xml: ET.Element | Text, *, indent: Text = "") -> Text:
    """Format an XML Element or string into a pretty-printed XML string.

    Parameters
    ----------
    _xml : ET.Element or str
        The XML Element or string to be pretty-printed.

    indent : str, optional
        The string used for indentation (default is an empty string).

    Returns
    -------
    str
        A pretty-printed XML string.
    """

    if isinstance(_xml, ET.Element):
        _xml_str = ET.tostring(_xml, encoding="utf-8", xml_declaration=False).decode(
            "utf-8"
        )
    else:
        _xml_str = _xml
    return minidom.parseString(_xml_str).toprettyxml(indent=indent)
