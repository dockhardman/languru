import json
import time
from typing import Any, Dict, List, Optional, Text, TypeVar, Union

import pymongo
from pydantic import BaseModel
from pymongo.synchronous.collection import Collection

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


def doc_exists(collection: "Collection", key: Text, value: Any) -> bool:
    return collection.count_documents({key: value}, limit=1) > 0


def fetch_docs_by_key_value(
    collection: "Collection",
    key: Text,
    value: Any,
    *,
    limit: int = 10,
    cast_to: PydanticModel,
) -> List[PydanticModel]:
    docs = []
    for doc in collection.find({key: value}).limit(limit):
        docs.append(cast_to.model_validate(doc))
    return docs


def any_doc_to_mongo(doc: BaseModel | Dict, *, use_ts: bool = False) -> Dict:
    _doc = json.loads(doc.model_dump_json()) if isinstance(doc, BaseModel) else doc
    if use_ts:
        _doc["_ts"] = _doc.pop("created_at") or int(time.time())
    return _doc


def create_mongo_index(
    collection: "Collection",
    key: Text,
    *,
    expire_after_seconds: Optional[int] = None,
    sort: Union[int, Text] = pymongo.ASCENDING,
):
    if expire_after_seconds is None:
        collection.create_index([(key, sort)])
    else:
        collection.create_index([(key, sort)], expireAfterSeconds=expire_after_seconds)
