import json
import re
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Text
from xml.sax.saxutils import escape as xml_escape


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


def to_xml(
    data: List[Dict] | Dict,
    *,
    tag_from_key: Text = "name",
    default_tag_name: Text = "object",
    wrapper_tag: Text = "objects",
    value_from_key: Optional[Text] = None
) -> "ET.Element":
    """Convert a list or dictionary of data into an XML Element.

    This function takes structured data and converts it into an XML format,
    creating a root element and child elements based on the provided keys.

    Parameters
    ----------
    data : List[Dict] | Dict
        A list of dictionaries or a single dictionary representing the data
        to be converted into XML. Each dictionary represents an object.

    tag_from_key : str, optional
        The key in the dictionary to use as the tag name for each child element.
        Defaults to "name". If the key is not present, the default_tag_name will be used.

    default_tag_name : str, optional
        The tag name to use for child elements if the tag_from_key is not found.
        Defaults to "object".

    wrapper_tag : str, optional
        The name of the root element. Defaults to "objects".

    value_from_key : str, optional
        The key in the dictionary to use for the text value of the child element.
        If not provided, the entire dictionary will be converted to a JSON string.

    Returns
    -------
    ET.Element
        The root XML element containing all child elements created from the input data.
    """  # noqa: E501

    data = data if isinstance(data, List) else [data]

    root = ET.Element("chat_record")
    for entry in data:

        if entry.get(tag_from_key):
            tag_name = entry[tag_from_key]
        else:
            tag_name = default_tag_name

        child = ET.SubElement(root, tag_name)

        if value_from_key is not None:
            child.text = xml_escape(str(entry.get(value_from_key)))
        else:
            child.text = xml_escape(json.dumps(entry, ensure_ascii=False))

    return root


def pretty_xml(
    _xml: ET.Element | Text, *, indent: Text = "", xml_declaration: bool = False
) -> Text:
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

    pretty_xml = minidom.parseString(_xml_str).toprettyxml(indent=indent)
    if not xml_declaration:
        pretty_xml = remove_xml_declaration(pretty_xml)
    return pretty_xml
