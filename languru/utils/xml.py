import json
from typing import Any, Dict, Optional, Sequence, Text, Union, cast
from xml.dom.minidom import DOMImplementation, getDOMImplementation

from pydantic import BaseModel


def to_xml_str(
    items: Union[Sequence[Dict[Text, Any]], Sequence["BaseModel"]],
    attributes_keys: Optional[Sequence[Text]] = None,
    content_key: Optional[Text] = None,
    element_name: Text = "item",
    root_name: Text = "items",
    indent: Text = "",
    remove_xml_declaration: bool = True,
) -> Text:
    """Convert a list of items to XML string.

    Parameters
    ----------
    items : Union[Sequence[Dict[Text, Any]], Sequence["BaseModel"]]
        List of items to convert.
    attributes_keys : Optional[Sequence[Text]], optional
        List of keys to use as attributes, by default None.
    content_key : Optional[Text], optional
        Key to use as content, by default None.
    element_name : Text, optional
        Name of the element, by default "item".
    root_name : Text, optional
        Name of the root element, by default "items".
    indent : Text, optional
        Indentation, by default "".
    remove_xml_declaration : bool, optional
        Whether to remove XML declaration, by default True.

    Returns
    -------
    Text
        XML string.

    Examples
    --------
    >>> items = [
    ...     {"id": 1, "name": "item1"},
    ...     {"id": 2, "name": "item2"},
    ...     {"id": 3, "name": "item3"},
    ... ]
    >>> xml_str = to_xml_str(items, attributes_keys=["id"], content_key="name")
    >>> print(xml_str)
    <items>
    <item id="1">item1</item>
    <item id="2">item2</item>
    <item id="3">item3</item>
    </items>
    """

    dom_impl = getDOMImplementation()
    dom_impl = cast(DOMImplementation, dom_impl)
    doc = dom_impl.createDocument(None, root_name, None)
    root = doc.documentElement

    for item in items:
        # Format data
        item_dict = (
            json.loads(item.model_dump_json())
            if isinstance(item, BaseModel)
            else dict(item)
        )
        # Create element
        item_ele = doc.createElement(element_name)
        # Add attributes
        for attributes_key in attributes_keys or []:
            if attributes_key in item_dict:
                item_ele.setAttribute(attributes_key, str(item_dict[attributes_key]))
        # Add content
        if content_key is not None:
            if content_key in item_dict:
                item_ele.appendChild(doc.createTextNode(str(item_dict[content_key])))
        root.appendChild(item_ele)

    # Return XML string
    out = doc.toprettyxml(indent=indent).strip()
    if remove_xml_declaration is True:
        # Remove (<?xml version="1.0" ?>)
        xml_version, out_prune = out.split("\n", 1)
        if xml_version.startswith("<?xml"):
            out = out_prune.strip()
    return out
