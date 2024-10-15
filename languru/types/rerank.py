from typing import List, Text

from pydantic import BaseModel


class RerankingResult(BaseModel):
    index: int
    document: Text
    relevance_score: float


class RerankingObject(BaseModel):
    results: List[RerankingResult]
    total_tokens: int
