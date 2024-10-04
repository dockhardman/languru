import hashlib
import time
from typing import TYPE_CHECKING, Any, Dict, List, Text

from cyksuid.v2 import ksuid
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from languru.documents.point import Point


class Document(BaseModel):
    document_id: Text = Field(default_factory=lambda: str(ksuid()))
    name: Text = Field(max_length=255)
    content: Text = Field(max_length=5000)
    content_md5: Text
    metadata: Dict[Text, Any] = Field(default_factory=dict)
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))

    @classmethod
    def from_content(cls, name: Text, content: Text) -> "Document":
        return cls.model_validate(
            {
                "content": content,
                "content_md5": hashlib.md5(content.encode()).hexdigest(),
                "name": name,
            }
        )

    def to_points(self) -> List[Point]:
        raise NotImplementedError
