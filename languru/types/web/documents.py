import hashlib
import time
from typing import TYPE_CHECKING, Optional, Text

import uuid_utils as uuid
from pydantic import BaseModel, Field
from yarl import URL

if TYPE_CHECKING:
    from googlesearch import SearchResult as GoogleSearchResult

    from languru.web.remote.google_search import SearchResult


def hash_text(text: Text) -> Text:
    """Hash a string using SHA-256."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Document(BaseModel):
    id: Text = Field(default_factory=lambda: str(uuid.uuid7()))


class HtmlDocument(Document):
    url: Text
    url_hash: Optional[Text] = Field(default=None)
    title: Text
    description: Text
    html_content: Optional[Text] = Field(default=None)
    markdown_content: Optional[Text] = Field(default=None)
    document_id: Optional[Text] = Field(default=None)
    created_at: int = Field(default_factory=lambda: int(time.time()))

    @classmethod
    def from_search_result(cls, result: "SearchResult | GoogleSearchResult"):
        url = str(URL(result.url))
        return cls(
            url=url,
            url_hash=hash_text(url),
            title=result.title,
            description=result.description,
        )
