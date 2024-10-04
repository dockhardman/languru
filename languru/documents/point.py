from typing import List, Text

from cyksuid.v2 import ksuid
from pydantic import BaseModel, Field


class Point(BaseModel):
    point_id: Text = Field(default_factory=lambda: str(ksuid()))
    document_id: Text
    document_md5: Text


class PointWithEmbedding(Point):
    embedding: List[float]
