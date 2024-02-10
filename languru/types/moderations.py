from typing import List, Optional, Text, Union

from pydantic import BaseModel, Field


class ModerationRequest(BaseModel):
    input: Union[Text, List[Text]]
    model: Optional[Text] = Field(
        default="text-moderation-latest",
        description=(
            "Two content moderations models are available: "
            + "text-moderation-stable and text-moderation-latest."
        ),
    )
