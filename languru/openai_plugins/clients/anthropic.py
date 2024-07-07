import os
import time
from typing import Dict, Generator, Iterable, List, Literal, Optional, Text, Union

import anthropic
import httpx
import openai
from anthropic.types.raw_content_block_delta_event import RawContentBlockDeltaEvent
from anthropic.types.raw_content_block_start_event import RawContentBlockStartEvent
from anthropic.types.raw_content_block_stop_event import RawContentBlockStopEvent
from anthropic.types.raw_message_delta_event import RawMessageDeltaEvent
from anthropic.types.raw_message_start_event import RawMessageStartEvent
from anthropic.types.raw_message_stop_event import RawMessageStopEvent
from anthropic.types.raw_message_stream_event import RawMessageStreamEvent
from anthropic.types.text_delta import TextDelta
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

from languru.config import logger
from languru.exceptions import CredentialsNotProvided
from languru.openai_plugins.clients.utils import openai_init_parameter_keys
from languru.types.chat.anthropic import AnthropicChatCompletionRequest
from languru.types.chat.completions import ChatCompletionRequest
from languru.types.models import MODELS_ANTHROPIC
from languru.utils.openai_utils import rand_chat_completion_id
from languru.utils.sse import simple_encode_sse


class AnthropicChatCompletions(Completions):

    _client: "AnthropicOpenAI"

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
        """Create a chat completion. This method is not implemented for
        Anthropic client.
        """

        if not messages:
            raise ValueError("The `messages` must not be empty")
        messages = list(messages)
        if len(list(messages)) == 0:
            raise ValueError("The `messages` must not be empty")

        anthropic_req = (
            AnthropicChatCompletionRequest.from_openai_chat_completion_request(
                ChatCompletionRequest.from_kwargs(
                    messages=messages, model=model, **kwargs
                )
            )
        )

        # Send request
        res_message = self._client.anthropic_client.messages.create(
            **anthropic_req.model_dump(exclude_none=True)
        )
        total_tokens = res_message.usage.input_tokens + res_message.usage.output_tokens
        finish_reason = "stop"
        if res_message.stop_reason == "end_turn":
            finish_reason = "stop"
        elif res_message.stop_reason == "max_tokens":
            finish_reason = "length"
        elif res_message.stop_reason == "stop_sequence":
            finish_reason = "stop"
        else:
            logger.warning(f"Unknown stop reason: {res_message.stop_reason}")

        # Return response
        return ChatCompletion.model_validate(
            {
                "id": res_message.id,
                "choices": [
                    {
                        "finish_reason": finish_reason,
                        "index": 0,
                        "message": {
                            "role": res_message.role,
                            "content": res_message.content[0].text,
                        },
                    }
                ],
                "created": int(time.time()),
                "model": res_message.model,
                "object": "chat.completion",
                "usage": {
                    "completion_tokens": res_message.usage.output_tokens,
                    "prompt_tokens": res_message.usage.input_tokens,
                    "total_tokens": total_tokens,
                },
            }
        )

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
        This method is not implemented for Anthropic client.
        Stream the chat completion response in chunks.
        """

        if not messages:
            raise ValueError("The `messages` must not be empty")
        messages = list(messages)
        if len(list(messages)) == 0:
            raise ValueError("The `messages` must not be empty")

        anthropic_req = (
            AnthropicChatCompletionRequest.from_openai_chat_completion_request(
                ChatCompletionRequest.from_kwargs(
                    messages=messages, model=model, **kwargs
                )
            )
        )

        # Send request
        input_output_tokens = {"input_tokens": 0, "output_tokens": 0}
        message_stream_manager = self._client.anthropic_client.messages.stream(
            **anthropic_req.model_dump(exclude_none=True, exclude={"stream"})
        )

        # Get the message stream, witch is considered name mangled.
        message_stream_event: "anthropic.Stream[RawMessageStreamEvent]" = (
            message_stream_manager.__dict__["_MessageStreamManager__api_request"]()
        )
        httpx_response_stream = ResponseStream(
            self.generator_generate_content_chunks(
                message_stream_event,
                model=model,
                input_output_tokens=input_output_tokens,
            )
        )
        httpx_response = httpx.Response(
            status_code=200,
            headers={"content-type": "text/plain"},
            stream=httpx_response_stream,
        )
        return Stream(
            cast_to=ChatCompletionChunk,
            response=httpx_response,
            client=self._client,
        )

    def generator_generate_content_chunks(
        self,
        message_stream_event: "anthropic.Stream[RawMessageStreamEvent]",
        *,
        model: Text,
        encoding: Text = "utf-8",
        created: Optional[int] = None,
        chat_completion_id: Optional[Text] = None,
        input_output_tokens: Optional[Dict[Text, int]] = None,
        **kwargs,
    ) -> Generator[bytes, None, None]:
        """Generate the chat completion chunks from the message stream.

        Parameters
        ----------
        message_stream_event : "anthropic.Stream[RawMessageStreamEvent]"
            The message stream event.
        model : Text
            The model name.
        encoding : Text, optional
            The encoding of the content, by default "utf-8".
        created : Optional[int], optional
            The timestamp of the chat completion, by default None.
        chat_completion_id : Optional[Text], optional
            The chat completion ID, by default None.
        input_output_tokens : Optional[Dict[Text, int]], optional
            The input and output tokens, by default None.

        Yields
        ------
        Generator[bytes, None, None]
            The generator yielding the chat completion chunks.
        """

        chat_completion_id = chat_completion_id or rand_chat_completion_id()
        created = created or int(time.time())
        input_output_tokens = input_output_tokens or {
            "input_tokens": 0,
            "output_tokens": 0,
        }
        finish_reason: Text = "stop"

        # Generate the chat response
        for event in message_stream_event:
            if isinstance(event, RawMessageStartEvent):
                chat_completion_id = event.message.id
                input_output_tokens["input_tokens"] = event.message.usage.input_tokens
            elif isinstance(event, RawContentBlockStartEvent):
                pass
            elif isinstance(event, RawContentBlockDeltaEvent):
                if isinstance(event.delta, TextDelta):
                    chunk = ChatCompletionChunk.model_validate(
                        {
                            "id": chat_completion_id,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "content": event.delta.text,
                                        "role": "assistant",
                                    },
                                }
                            ],
                            "created": created,
                            "model": model,
                            "object": "chat.completion.chunk",
                        }
                    )
                    yield simple_encode_sse(chunk, encoding=encoding)
                else:
                    logger.warning(f"Unhandled delta type: {event.delta} yet.")
            elif isinstance(event, RawContentBlockStopEvent):
                pass
            elif isinstance(event, RawMessageDeltaEvent):
                input_output_tokens["output_tokens"] = event.usage.output_tokens
                if event.delta.stop_reason == "end_turn":
                    finish_reason = "stop"
                elif event.delta.stop_reason == "max_tokens":
                    finish_reason = "length"
                elif event.delta.stop_reason == "stop_sequence":
                    finish_reason = "stop"
                else:
                    logger.warning(f"Unknown stop reason: {event.delta.stop_reason}")
            elif isinstance(event, RawMessageStopEvent):
                pass
            else:
                logger.warning(f"Unhandled event type: {event} yet.")

        # Send the final chunk with finish_reason
        chunk = ChatCompletionChunk.model_validate(
            {
                "id": chat_completion_id,
                "choices": [{"delta": {}, "finish_reason": finish_reason, "index": 0}],
                "created": created,
                "model": model,
                "object": "chat.completion.chunk",
            }
        )
        yield simple_encode_sse(chunk, encoding=encoding)

        # End the stream
        yield simple_encode_sse("[DONE]", encoding=encoding)


class AnthropicChat(OpenAIResources.Chat):
    @cached_property
    def completions(self) -> AnthropicChatCompletions:
        return AnthropicChatCompletions(self._client)


class AnthropicModels(OpenAIResources.Models):

    supported_models = frozenset(MODELS_ANTHROPIC)

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

    anthropic_client: anthropic.Anthropic

    def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
        api_key = (
            api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("CLAUDE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            raise CredentialsNotProvided("Anthropic API key is not provided")
        kwargs["api_key"] = api_key
        kwargs = {k: v for k, v in kwargs.items() if k in openai_init_parameter_keys}

        super().__init__(**kwargs)

        self.chat = AnthropicChat(self)
        self.models = AnthropicModels(self)

        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
