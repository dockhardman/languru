from typing import Dict, Iterable, Optional, Text

from openai.types.beta import assistant_create_params
from openai.types.beta.assistant_response_format_option_param import (
    AssistantResponseFormatOptionParam,
)
from openai.types.beta.assistant_tool_param import AssistantToolParam
from pydantic import BaseModel, Field


class AssistantsCreateRequest(BaseModel):
    model: Text = Field(..., description="ID of the model to use")
    description: Optional[Text] = Field(
        None, description="The description of the assistant"
    )
    instructions: Optional[Text] = Field(
        None, description="The system instructions that the assistant uses"
    )
    metadata: Optional[Dict] = Field(
        None, description="Set of 16 key-value pairs that can be attached to an object"
    )
    name: Optional[Text] = Field(None, description="The name of the assistant")
    response_format: Optional[AssistantResponseFormatOptionParam] = Field(
        None, description="Specifies the format that the model must output"
    )
    temperature: Optional[float] = Field(
        None, description="What sampling temperature to use"
    )
    tool_resources: Optional[assistant_create_params.ToolResources] = Field(
        None, description="A set of resources that are used by the assistant's tools"
    )
    tools: Optional[Iterable[AssistantToolParam]] = Field(
        None, description="A list of tool enabled on the assistant"
    )
    top_p: Optional[float] = Field(
        None, description="An alternative to sampling with temperature"
    )


class AssistantsUpdateRequest(BaseModel):
    assistant_id: Text = Field(..., description="The ID of the assistant to update")
    model: Optional[Text] = Field(None, description="ID of the model to use")
    description: Optional[Text] = Field(
        None, description="The description of the assistant"
    )
    instructions: Optional[Text] = Field(
        None, description="The system instructions that the assistant uses"
    )
    metadata: Optional[Dict] = Field(
        None, description="Set of 16 key-value pairs that can be attached to an object"
    )
    name: Optional[Text] = Field(None, description="The name of the assistant")
    response_format: Optional[AssistantResponseFormatOptionParam] = Field(
        None, description="Specifies the format that the model must output"
    )
    temperature: Optional[float] = Field(
        None, description="What sampling temperature to use"
    )
    tool_resources: Optional[assistant_create_params.ToolResources] = Field(
        None, description="A set of resources that are used by the assistant's tools"
    )
    tools: Optional[Iterable[AssistantToolParam]] = Field(
        None, description="A list of tool enabled on the assistant"
    )
    top_p: Optional[float] = Field(
        None, description="An alternative to sampling with temperature"
    )
