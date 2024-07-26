from typing import Dict, List, Optional, Text

from openai.types.beta.assistant import ToolResources
from openai.types.beta.assistant_response_format_option import (
    AssistantResponseFormatOption,
)
from openai.types.beta.assistant_tool import AssistantTool
from pydantic import BaseModel, Field


class AssistantUpdateRequest(BaseModel):
    description: Optional[Text] = Field(
        default=None, description="The description of the assistant."
    )
    instructions: Optional[Text] = Field(
        default=None, description="The system instructions that the assistant uses."
    )
    metadata: Optional[Dict[Text, Text]] = Field(
        default=None,
        description="Set of 16 key-value pairs that can be attached to an object.",
    )
    model: Optional[Text] = Field(default=None, description="ID of the model to use.")
    name: Optional[Text] = Field(default=None, description="The name of the assistant.")
    response_format: Optional[AssistantResponseFormatOption] = Field(
        default=None, description="Specifies the format that the model must output."
    )
    temperature: Optional[float] = Field(
        default=None,
        le=2.0,
        ge=0.0,
        description="What sampling temperature to use, between 0 and 2.",
    )
    tool_resources: Optional[ToolResources] = Field(
        default=None,
        description="A set of resources that are used by the assistant's tools.",
    )
    tools: List[AssistantTool] = Field(
        default_factory=list, description="A list of tool enabled on the assistant."
    )
    top_p: Optional[float] = Field(
        default=None,
        description="An alternative to sampling with temperature, called nucleus sampling.",  # noqa: E501
    )
