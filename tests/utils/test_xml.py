from textwrap import dedent
from typing import Dict, Text

import pytest
from pydantic import BaseModel

from languru.utils.xml import to_xml_str


class Item(BaseModel):
    id: int
    name: Text
    type: Text


simple_items = [
    {"id": 1, "name": "item1"},
    {"id": 2, "name": "item2"},
    {"id": 3, "name": "item3"},
]
simple_items_xml = dedent(
    """
    <items>
    <item id="1">item1</item>
    <item id="2">item2</item>
    <item id="3">item3</item>
    </items>
    """
).strip()
extra_items = [
    {"id": 1, "name": "Allen", "type": "employee"},
    {"id": 2, "name": "Alice", "type": "employee"},
    {"id": 3, "name": "Alex", "type": "manager"},
]
extra_items_xml = dedent(
    """
    <users>
        <user id="1" type="employee">Allen</user>
        <user id="2" type="employee">Alice</user>
        <user id="3" type="manager">Alex</user>
    </users>
    """
).strip()
model_items = [
    Item(id=1, name="Allen", type="employee"),
    Item(id=3, name="Alex", type="manager"),
]
model_items_xml = dedent(
    """
    <users>
    <user id="1" type="employee">Allen</user>
    <user id="3" type="manager">Alex</user>
    </users>
    """
).strip()


@pytest.mark.parametrize(
    "items, parameters, expected_xml_str",
    [
        (
            simple_items,
            {"attributes_keys": ["id"], "content_key": "name"},
            simple_items_xml,
        ),
        (
            extra_items,
            {
                "attributes_keys": ["id", "type"],
                "content_key": "name",
                "element_name": "user",
                "root_name": "users",
                "indent": "    ",
            },
            extra_items_xml,
        ),
        (
            model_items,
            {
                "attributes_keys": ["id", "type"],
                "content_key": "name",
                "element_name": "user",
                "root_name": "users",
            },
            model_items_xml,
        ),
    ],
)
def test_to_xml_str(items, parameters: Dict, expected_xml_str: Text):
    xml_str = to_xml_str(items, **parameters)
    assert xml_str == expected_xml_str
