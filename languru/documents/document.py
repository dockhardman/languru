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

import numpy as np
from cyksuid.v2 import ksuid
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from openai import OpenAI

    from languru.documents._client import DocumentQuerySet, PointQuerySet


PointType = TypeVar("PointType", bound="Point")


class Point(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    TABLE_NAME: ClassVar[Text] = "points"
    EMBEDDING_MODEL: ClassVar[Text] = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: ClassVar[int] = 512

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
    embedding: List[float] = Field(
        max_length=512,
        min_length=512,
        description="The embedding of the point.",
        default_factory=lambda: [0.0] * 512,
    )

    @classmethod
    def query_set(cls) -> "PointQuerySet":
        from languru.documents._client import PointQuerySet

        return PointQuerySet(cls)

    objects: "PointQuerySet" = property(query_set)  # type: ignore

    def is_embedded(self) -> bool:
        return bool(np.all(np.array(self.embedding) == 0.0))


class Document(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    TABLE_NAME: ClassVar[Text] = "documents"
    POINT_TYPE: ClassVar[Type[Point]] = Point

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

    @classmethod
    def query_set(cls) -> "DocumentQuerySet":
        from languru.documents._client import DocumentQuerySet

        return DocumentQuerySet(cls)

    objects: "DocumentQuerySet" = property(query_set)  # type: ignore

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
        self,
        *,
        openai_client: Optional["OpenAI"] = None,
        embedding: Optional[List[float]] = None,
    ) -> List["Point"]:
        self.refresh_md5()

        params: Dict = {
            "document_id": self.document_id,
            "document_md5": self.content_md5,
        }

        if embedding is not None:
            params["embedding"] = embedding
        elif openai_client is not None:
            _emb_res = openai_client.embeddings.create(
                input=self.to_embedded_content(),
                model=self.POINT_TYPE.EMBEDDING_MODEL,
                dimensions=self.POINT_TYPE.EMBEDDING_DIMENSIONS,
            )
            embedding = _emb_res.data[0].embedding

        point_out = self.POINT_TYPE.model_validate(params)

        return [point_out]

    def to_embedded_content(self, *args, **kwargs) -> Text:
        return self.content.strip()

    def refresh_md5(self) -> "Document":
        self.content = self.content.strip()
        new_md5 = self.hash_content(self.content)
        if self.content_md5 != new_md5:
            self.content_md5 = new_md5
            self.updated_at = int(time.time())
        return self
