from typing import Dict, List, Literal, Optional, Text, Union

from openai.types.beta.assistant import ToolResources
from openai.types.beta.threads.annotation import Annotation as OpenaiAnnotation
from openai.types.beta.threads.image_file import ImageFile
from openai.types.beta.threads.image_url import ImageURL
from openai.types.beta.threads.message import AttachmentTool
from openai.types.beta.threads.text import Text as OpenaiText
from openai.types.beta.threads.text_content_block import (
    TextContentBlock as OpenaiTextContentBlock,
)
from pydantic import BaseModel, Field


class TextContentBlockText(OpenaiText):
    annotations: List[OpenaiAnnotation] = Field(
        default_factory=list, description="A list of annotations for the text."
    )


class TextContentBlock(OpenaiTextContentBlock):
    text: TextContentBlockText
    type: Literal["text"] = Field(default="text", description="Always `text`.")


MessageContent = Union[ImageFile, ImageURL, TextContentBlockText]


class ThreadsMessageCreate(BaseModel):
    content: Optional[Union[Text, List[MessageContent]]] = Field(
        default=None, description="The text contents of the message."
    )
    role: Literal["user", "assistant"] = Field(
        ..., description="The role of the entity that is creating the message."
    )
    attachments: Optional[List[AttachmentTool]] = Field(
        default=None,
        description=(
            "A list of files attached to the message, "
            + "and the tools they should be added to."
        ),
    )
    metadata: Optional[Dict[Text, Text]] = Field(
        default=None,
        description="Set of 16 key-value pairs that can be attached to an object.",
    )


class ThreadCreateRequest(BaseModel):
    messages: Optional[List[ThreadsMessageCreate]] = Field(
        default=None,
        description="A list of messages to start the thread with.",
    )
    metadata: Optional[Dict[Text, Text]] = Field(
        default=None,
        description="Set of 16 key-value pairs that can be attached to an object.",
    )
    tool_resources: Optional[ToolResources] = Field(
        default=None,
        description=(
            "A set of resources that are made available to "
            + "the assistant's tools in this thread."
        ),
    )
