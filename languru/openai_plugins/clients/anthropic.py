import os
import time
import uuid
from typing import Dict, Generator, Iterable, List, Literal, Optional, Text, Union

import anthropic
import google.generativeai as genai
import httpx
import openai
from google.api_core.exceptions import NotFound as GoogleNotFound
from google.generativeai.types import generation_types
from google.generativeai.types.content_types import ContentDict
from httpx._transports.default import ResponseStream
from openai import OpenAI
from openai import resources as OpenAIResources
from openai._compat import cached_property
from openai._streaming import Stream
from openai._types import NOT_GIVEN, Body, Headers, NotGiven, Query
from openai._utils import required_args
from openai.pagination import SyncPage
from openai.resources.chat.completions import Completions
from openai.types.chat import completion_create_params
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_stream_options_param import (
    ChatCompletionStreamOptionsParam,
)
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.chat_model import ChatModel
from openai.types.model import Model

from languru.openai_plugins.clients.utils import openai_init_parameter_keys
from languru.utils.openai_utils import rand_chat_completion_id
from languru.utils.sse import simple_encode_sse


class AnthropicChatCompletions(Completions):
    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def create(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        stream_options: (
            Optional[ChatCompletionStreamOptionsParam] | NotGiven
        ) = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        if stream is True:
            return self._create_stream(
                messages=messages,
                model=model,
                frequency_penalty=frequency_penalty,
                function_call=function_call,
                functions=functions,
                logit_bias=logit_bias,
                logprobs=logprobs,
                max_tokens=max_tokens,
                n=n,
                presence_penalty=presence_penalty,
                response_format=response_format,
                seed=seed,
                stop=stop,
                stream=True,
                stream_options=stream_options,
                temperature=temperature,
                tool_choice=tool_choice,
                tools=tools,
                top_logprobs=top_logprobs,
                top_p=top_p,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                **kwargs,
            )
        return self._create(
            messages=messages,
            model=model,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_tokens=max_tokens,
            n=n,
            presence_penalty=presence_penalty,
            response_format=response_format,
            seed=seed,
            stop=stop,
            stream=False,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **kwargs,
        )

    def _create(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        stream: Literal[False] = False,
        stream_options: (
            Optional[ChatCompletionStreamOptionsParam] | NotGiven
        ) = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> ChatCompletion:
        """Create a chat completion. This method is not implemented for Google GenAI."""

        if not messages:
            raise ValueError("The `messages` must not be empty")
        messages = list(messages)
        if len(list(messages)) == 0:
            raise ValueError("The `messages` must not be empty")

        pass

    def _create_stream(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        stream: Literal[True] = True,
        stream_options: (
            Optional[ChatCompletionStreamOptionsParam] | NotGiven
        ) = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> Stream[ChatCompletionChunk]:
        """Create a chat completion stream.
        This method is not implemented for Google GenAI.
        Stream the chat completion response in chunks.
        """

        if not messages:
            raise ValueError("The `messages` must not be empty")
        messages = list(messages)
        if len(list(messages)) == 0:
            raise ValueError("The `messages` must not be empty")

        pass


class AnthropicChat(OpenAIResources.Chat):
    @cached_property
    def completions(self) -> AnthropicChatCompletions:
        return AnthropicChatCompletions(self._client)


class AnthropicModels(OpenAIResources.Models):

    supported_models = frozenset(
        [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
    )

    def retrieve(
        self,
        model: str,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> "Model":
        if model in self.supported_models:
            return Model.model_validate(
                {
                    "id": model,
                    "created": int(time.time()),
                    "object": "model",
                    "owned_by": "anthropic",
                }
            )
        else:
            error_message = (
                f"Model {model} not found. Supported models are {self.supported_models}"
            )
            raise openai.NotFoundError(
                error_message,
                response=httpx.Response(status_code=404, text=error_message),
                body=None,
            )

    def list(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> "SyncPage[Model]":
        created = int(time.time())
        models = [
            Model.model_validate(
                {
                    "id": model,
                    "created": created,
                    "object": "model",
                    "owned_by": "anthropic",
                }
            )
            for model in self.supported_models
        ]
        return SyncPage(data=models, object="list")


class AnthropicOpenAI(OpenAI):
    chat: AnthropicChat
    models: AnthropicModels

    def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
        api_key = (
            api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("CLAUDE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            raise ValueError("Anthropic API key is not provided")
        kwargs["api_key"] = api_key
        kwargs = {k: v for k, v in kwargs.items() if k in openai_init_parameter_keys}

        super().__init__(**kwargs)

        self.chat = AnthropicChat(self)
        self.models = AnthropicModels(self)

        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
