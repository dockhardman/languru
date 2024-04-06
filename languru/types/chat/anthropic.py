from typing import List, Optional, Text

from anthropic.types.message_param import MessageParam
from pydantic import BaseModel, ConfigDict, Field

from languru.types.chat.completions import ChatCompletionRequest


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow")


class ToolInputSchema(BaseModel):
    type: Text
    properties: dict
    required: List[Text]


class Tool(BaseModel):
    name: Text
    description: Optional[Text] = None
    input_schema: ToolInputSchema


class AnthropicChatCompletionRequest(BaseModel):
    model: Text
    messages: List[MessageParam]
    max_tokens: int = 800
    metadata: Optional[Metadata] = None
    stop_sequences: Optional[List[Text]] = None
    stream: Optional[bool] = None
    system: Optional[Text] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_k: Optional[int] = None
    top_p: Optional[float] = None

    @classmethod
    def from_openai_chat_completion_request(
        cls, request: "ChatCompletionRequest"
    ) -> "AnthropicChatCompletionRequest":
        request = request.model_copy(deep=True)
        sys_message = None
        sys_message_idx = None
        for idx, m in enumerate(request.messages):
            if m.role == "system":
                sys_message_idx = idx
                break
        if sys_message_idx is not None:
            sys_message = request.messages.pop(sys_message_idx)
        params = request.model_dump(exclude_none=True)
        params["system"] = sys_message.content if sys_message is not None else None
        return cls.model_validate(params)
