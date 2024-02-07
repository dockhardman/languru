from typing import Dict, List, Optional, Text, Union

from pydantic import BaseModel, Field


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


class ChatCompletionRequest(BaseModel):
    messages: List[Message] = Field(
        ..., description="A list of messages comprising the conversation so far"
    )
    model: Text = Field(..., description="ID of the model to use")
    frequency_penalty: Optional[float] = Field(
        0, description="Penalize frequencies of new tokens"
    )
    logit_bias: Optional[Dict[int, float]] = Field(
        None, description="Modify the likelihood of specified tokens"
    )
    logprobs: Optional[bool] = Field(
        False, description="Whether to return log probabilities or not"
    )
    top_logprobs: Optional[int] = Field(
        None, ge=0, le=5, description="Number of most likely tokens to return"
    )
    max_tokens: Optional[int] = Field(
        None, description="Maximum number of tokens that can be generated"
    )
    n: Optional[int] = Field(
        1, description="Number of chat completion choices to generate"
    )
    presence_penalty: Optional[float] = Field(
        0, description="Penalize new tokens based on their presence"
    )
    response_format: Optional[ResponseFormat] = None
    seed: Optional[int] = Field(None, description="Seed for deterministic sampling")
    stop: Optional[Union[Text, List[Text]]] = Field(
        None, description="Sequences where the API will stop generating tokens"
    )
    stream: Optional[bool] = Field(
        False, description="If true, partial message deltas will be sent"
    )
    temperature: Optional[float] = Field(
        1, ge=0, le=2, description="Sampling temperature"
    )
    top_p: Optional[float] = Field(
        1, description="Top p probability mass for nucleus sampling"
    )
    tools: Optional[List[Text]] = Field(
        None, description="List of tools the model may call"
    )
    tool_choice: Optional[Union[Text, FunctionChoice]] = Field(
        None, description="Controls which function is called by the model"
    )
    user: Optional[Text] = Field(
        None, description="A unique identifier representing your end-user"
    )
