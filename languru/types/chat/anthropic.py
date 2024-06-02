from typing import List, Literal, Optional, Text, Union

from pydantic import BaseModel, ConfigDict, Field

from languru.config import logger
from languru.types.chat.completions import ChatCompletionRequest


class Source(BaseModel):
    type: Literal["base64"]
    media_type: str
    data: str


class ContentBlock(BaseModel):
    type: Literal["text", "image"]
    text: Optional[str] = None
    source: Optional[Source] = None


class MessageParam(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, List[ContentBlock]]


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
    stream: bool = False
    system: Optional[Text] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_k: Optional[int] = None
    top_p: Optional[float] = None

    @classmethod
    def from_openai_chat_completion_request(
        cls, request: "ChatCompletionRequest"
    ) -> "AnthropicChatCompletionRequest":
        request = request.model_copy(deep=True)

        system: Optional[Text] = None
        sys_message_indexes: List[int] = []
        messages: List[MessageParam] = []
        temperature: float = 1.0 if request.temperature is None else request.temperature

        for idx, m in enumerate(request.messages):
            if m.role == "system":
                sys_message_indexes.append(idx)
            elif m.role == "user":
                messages.append(MessageParam(role="user", content=m.content))
            elif m.role == "assistant":
                messages.append(MessageParam(role="assistant", content=m.content))
            else:
                logger.warning(f"Unknown role: {m.role}")

        system = "\n\n".join(
            [request.messages[sys_idx].content for sys_idx in sys_message_indexes]
        )

        return cls.model_validate(
            {
                "model": request.model,
                "messages": messages,
                "max_tokens": request.max_tokens or 800,
                "metadata": None,
                "stop_sequences": request.stop,
                "stream": request.stream or False,
                "system": system.strip() or None,
                "temperature": min(max(temperature, 0.0), 1.0),
                "top_k": None,
                "top_p": request.top_p,
            }
        )
