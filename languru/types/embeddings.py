from typing import List, Optional, Text, Union

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    input: Union[Text, List[Union[Text, List[Text]]]]
    model: Text
    encoding_format: Optional[Text] = Field(
        default="float", description="The format to return the embeddings in."
    )
    dimensions: Optional[int] = Field(
        default=None,
        description="The number of dimensions for the output embeddings.",
        gt=0,
    )
    user: Optional[Text] = Field(
        default=None, description="A unique identifier representing your end-user."
    )
