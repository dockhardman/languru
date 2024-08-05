from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Text, Union

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from openai.types.beta.threads.message import Message as ThreadsMessage
    from openai.types.beta.threads.run import Run as ThreadsRun


class LogitBias(BaseModel):
    # Assuming token ID as integer and bias value as float, adjust types if needed
    token_id: int = Field(..., description="Token ID")
    bias: float = Field(..., ge=-100, le=100, description="Bias value from -100 to 100")


class ResponseFormat(BaseModel):
    type: Text = Field(
        ...,
        description='Type of response format, e.g., "json_object" for JSON mode',
    )


class FunctionChoice(BaseModel):
    type: Text = Field(..., description="Specifies the type, e.g., 'function'")
    function: Optional[Dict[Text, Text]] = None


class Message(BaseModel):
    role: Text
    content: Text

    @classmethod
    def from_openai_threads_message(cls, message: "ThreadsMessage"):
        """Builds a Message object from an OpenAI Threads message"""

        message_text = ""
        for message_content in message.content:
            if message_content.type == "text":
                message_text += message_content.text.value
        return cls.model_validate(
            {"role": message.role, "content": message_text.strip()}
        )


class ChatCompletionRequest(BaseModel):
    messages: List[Message] = Field(
        ..., description="A list of messages comprising the conversation so far"
    )
    model: Text = Field(..., description="ID of the model to use")
    frequency_penalty: Optional[float] = Field(
        default=None, description="Penalize frequencies of new tokens"
    )
    logit_bias: Optional[Dict[int, float]] = Field(
        default=None, description="Modify the likelihood of specified tokens"
    )
    logprobs: Optional[bool] = Field(
        default=None, description="Whether to return log probabilities or not"
    )
    top_logprobs: Optional[int] = Field(
        default=None, ge=0, le=5, description="Number of most likely tokens to return"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum number of tokens that can be generated"
    )
    n: Optional[int] = Field(
        default=None, description="Number of chat completion choices to generate"
    )
    presence_penalty: Optional[float] = Field(
        default=None, description="Penalize new tokens based on their presence"
    )
    response_format: Optional[ResponseFormat] = Field(
        default=None, description="Format that the model must output"
    )
    seed: Optional[int] = Field(
        default=None, description="Seed for deterministic sampling"
    )
    stop: Optional[Union[Text, List[Text]]] = Field(
        default=None, description="Sequences where the API will stop generating tokens"
    )
    stream: Optional[bool] = Field(
        default=None, description="If true, partial message deltas will be sent"
    )
    temperature: Optional[float] = Field(
        default=None, ge=0, le=2, description="Sampling temperature"
    )
    top_p: Optional[float] = Field(
        default=None, description="Top p probability mass for nucleus sampling"
    )
    tools: Optional[List[Text]] = Field(
        default=None, description="List of tools the model may call"
    )
    tool_choice: Optional[Union[Text, FunctionChoice]] = Field(
        default=None, description="Controls which function is called by the model"
    )
    user: Optional[Text] = Field(
        default=None, description="A unique identifier representing your end-user"
    )

    @classmethod
    def from_kwargs(cls, **kwargs) -> "ChatCompletionRequest":
        if "messages" not in kwargs:
            raise ValueError("Parameter messages is required")
        if "model" not in kwargs:
            raise ValueError("Parameter model is required")
        return cls.model_validate(kwargs)

    @classmethod
    def from_openai_threads_run(
        cls,
        run: "ThreadsRun",
        messages: Sequence["ThreadsMessage"],
        *,
        stream: Optional[bool] = None
    ):
        """Builds a ChatCompletionRequest object from an OpenAI Threads run"""

        chat_messages: List["Message"] = []
        if run.instructions:
            chat_messages.append(
                Message.model_validate({"role": "system", "content": run.instructions})
            )
        for m in messages:
            chat_messages.append(Message.from_openai_threads_message(m))
        chat_completion_request = ChatCompletionRequest.model_validate(
            {
                "messages": chat_messages,
                "model": run.model,
                "temperature": run.temperature,
            }
        )
        if stream is not None:
            chat_completion_request.stream = stream
        return chat_completion_request
