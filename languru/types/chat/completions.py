from typing import Dict, List, Literal, Optional, Text, Union

import httpx
from openai._types import NOT_GIVEN, Body, Headers, NotGiven, Query
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
    completion_create_params,
)
from pydantic import BaseModel, ConfigDict, Field


class ChatCompletionCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, extra="allow", str_strip_whitespace=True
    )

    messages: List[ChatCompletionMessageParam] = Field(
        ...,
        description="The messages that the model will use to generate a response.",
    )
    model: (
        Literal[
            "gpt-4-0125-preview",
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-4-32k-0613",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-16k-0613",
        ]
        | Text
    ) = Field(...)
    frequency_penalty: Optional[float] | NotGiven = Field(
        NOT_GIVEN,
        description=(
            "The frequency penalty to apply to the model's output. "
            + "Higher values will decrease the likelihood of the model repeating the same response."
        ),
    )
    function_call: completion_create_params.FunctionCall | NotGiven = Field(
        NOT_GIVEN, description="The function to call."
    )
    functions: List[completion_create_params.Function] | NotGiven = Field(
        NOT_GIVEN, description="The functions to call."
    )
    logit_bias: Optional[Dict[Text, int]] | NotGiven = Field(
        NOT_GIVEN, description="The logit bias to apply to the model's output."
    )
    logprobs: Optional[bool] | NotGiven = Field(
        NOT_GIVEN,
        description="Whether to return the log probabilities of the generated tokens.",
    )
    max_tokens: Optional[int] | NotGiven = Field(
        NOT_GIVEN, description="The maximum number of tokens to generate."
    )
    n: Optional[int] | NotGiven = Field(
        NOT_GIVEN, description="The number of completions to generate."
    )
    presence_penalty: Optional[float] | NotGiven = Field(
        NOT_GIVEN,
        description=(
            "The presence penalty to apply to the model's output. "
            + "Higher values will decrease the likelihood of the model repeating the same response."
        ),
    )
    response_format: completion_create_params.ResponseFormat | NotGiven = Field(
        NOT_GIVEN, description="The format of the response."
    )
    seed: Optional[int] | NotGiven = Field(
        NOT_GIVEN,
        description="The seed to use for the model's random number generator.",
    )
    stop: Union[Optional[Text], List[Text]] | NotGiven = Field(
        NOT_GIVEN, description="The tokens at which to stop the generation."
    )
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = Field(
        NOT_GIVEN, description="Whether to stream the response."
    )
    temperature: Optional[float] | NotGiven = Field(
        NOT_GIVEN,
        description="The temperature to use for the model's random number generator.",
    )
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = Field(
        NOT_GIVEN, description="The tool choice to use."
    )
    tools: List[ChatCompletionToolParam] | NotGiven = Field(
        NOT_GIVEN, description="The tools to use."
    )
    top_logprobs: Optional[int] | NotGiven = Field(
        NOT_GIVEN, description="The number of log probabilities to return."
    )
    top_p: Optional[float] | NotGiven = Field(
        NOT_GIVEN, description="The nucleus sampling probability."
    )
    user: Text | NotGiven = Field(NOT_GIVEN, description="The user to use.")
    extra_headers: Headers | None = Field(None, description="The extra headers to use.")
    extra_query: Query | None = Field(None, description="The extra query to use.")
    extra_body: Body | None = Field(None, description="The extra body to use.")
    timeout: float | httpx.Timeout | None | NotGiven = Field(
        NOT_GIVEN, description="The timeout to use."
    )
