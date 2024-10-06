import hashlib
import time
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Text,
    Type,
    TypeVar,
)

from cyksuid.v2 import ksuid
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from openai import OpenAI

    from languru.documents._client import DocumentClient


PointType = TypeVar("PointType", bound="Point")


class Point(BaseModel):
    point_id: Text = Field(
        default_factory=lambda: f"pt_{str(ksuid())}",
        description="The unique and primary ID of the point.",
    )
    document_id: Text = Field(
        description="The ID of the document that the point belongs to."
    )
    document_md5: Text = Field(
        description="The MD5 hash of the document that the point belongs to."
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        description="The embedding of the point.",
    )

    EMBEDDING_MODEL: ClassVar[Text] = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: ClassVar[int] = 512


class Document(BaseModel):
    document_id: Text = Field(
        default_factory=lambda: f"doc_{str(ksuid())}",
        description="The unique and primary ID of the document.",
    )
    name: Text = Field(max_length=255, description="The unique name of the document.")
    content: Text = Field(max_length=5000, description="The content of the document.")
    content_md5: Text = Field(description="The MD5 hash of the document content.")
    metadata: Dict[Text, Any] = Field(
        default_factory=dict, description="Any additional metadata for the document."
    )
    created_at: int = Field(
        default_factory=lambda: int(time.time()),
        description="The timestamp of when the document was created.",
    )
    updated_at: int = Field(
        default_factory=lambda: int(time.time()),
        description="The timestamp of when the document was last updated.",
    )

    model_config = ConfigDict(str_strip_whitespace=True)
    point_type: ClassVar[Type[Point]] = Point

    @classmethod
    def from_content(cls, name: Text, content: Text) -> "Document":
        return cls.model_validate(
            {
                "content": content,
                "content_md5": cls.hash_content(content),
                "name": name,
            }
        )

    @classmethod
    def hash_content(cls, content: Text) -> Text:
        return hashlib.md5(content.strip().encode("utf-8")).hexdigest()

    def to_points(
        self, *, openai_client: "OpenAI", embedding: Optional[List[float]] = None
    ) -> List["Point"]:
        if embedding is None:
            _emb_res = openai_client.embeddings.create(
                input=self.to_embedded_content(),
                model=self.point_type.EMBEDDING_MODEL,
                dimensions=self.point_type.EMBEDDING_DIMENSIONS,
            )
            embedding = _emb_res.data[0].embedding

        return [
            self.point_type.model_validate(
                {
                    "document_id": self.document_id,
                    "document_md5": self.content_md5,
                    "embedding": embedding,
                }
            )
        ]

    def to_embedded_content(self, *args, **kwargs) -> Text:
        return self.content.strip()

    def refresh_md5(self) -> "Document":
        self.content = self.content.strip()
        new_md5 = self.hash_content(self.content)
        if self.content_md5 != new_md5:
            self.content_md5 = new_md5
            self.updated_at = int(time.time())
        return self
