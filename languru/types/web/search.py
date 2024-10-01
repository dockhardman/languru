from typing import Text

from pydantic import BaseModel


class SearchResult(BaseModel):
    url: Text
    title: Text
    description: Text
