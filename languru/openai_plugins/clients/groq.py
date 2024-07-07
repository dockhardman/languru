import json
import os
from typing import Dict, Generator, Iterable, List, Literal, Optional, Text, Union

import httpx
import openai
from groq import Groq
from groq import NotFoundError as GroqNotFoundError
from groq._streaming import Stream as GroqStream
from groq._types import NOT_GIVEN as GroqNotGiven
from groq.types.chat.chat_completion_chunk import (
    ChatCompletionChunk as GroqChatCompletionChunk,
)
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

from languru.exceptions import CredentialsNotProvided
from languru.openai_plugins.clients.utils import openai_init_parameter_keys
from languru.types.models import MODELS_GROQ
from languru.utils.sse import simple_encode_sse


class GroqChatCompletions(Completions):

    _client: "GroqOpenAI"

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
        Groq client.
        """

        if not messages:
            raise ValueError("The `messages` must not be empty")
        messages = list(messages)
        if len(list(messages)) == 0:
            raise ValueError("The `messages` must not be empty")

        # Send request
        params = json.loads(
            json.dumps(
                {
                    k: v
                    for k, v in (
                        ("frequency_penalty", frequency_penalty),
                        ("function_call", function_call),
                        ("functions", functions),
                        ("logit_bias", logit_bias),
                        ("logprobs", logprobs),
                        ("max_tokens", max_tokens),
                        ("n", n),
                        ("presence_penalty", presence_penalty),
                        ("response_format", response_format),
                        ("seed", seed),
                        ("stop", stop),
                        ("temperature", temperature),
                        ("tool_choice", tool_choice),
                        ("tools", tools),
                        ("top_logprobs", top_logprobs),
                        ("top_p", top_p),
                        ("user", user),
                    )
                    if v is not None and v is not NOT_GIVEN and v is not GroqNotGiven
                }
            )
        )
        res_message = self._client.groq_client.chat.completions.create(
            messages=messages, model=model, stream=False, **params  # type: ignore
        )

        # Return response
        return ChatCompletion.model_validate(res_message.model_dump(exclude_none=True))

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
        This method is not implemented for Groq client.
        Stream the chat completion response in chunks.
        """

        if not messages:
            raise ValueError("The `messages` must not be empty")
        messages = list(messages)
        if len(list(messages)) == 0:
            raise ValueError("The `messages` must not be empty")

        # Send request
        params = json.loads(
            json.dumps(
                {
                    k: v
                    for k, v in (
                        ("frequency_penalty", frequency_penalty),
                        ("function_call", function_call),
                        ("functions", functions),
                        ("logit_bias", logit_bias),
                        ("logprobs", logprobs),
                        ("max_tokens", max_tokens),
                        ("n", n),
                        ("presence_penalty", presence_penalty),
                        ("response_format", response_format),
                        ("seed", seed),
                        ("stop", stop),
                        ("temperature", temperature),
                        ("tool_choice", tool_choice),
                        ("tools", tools),
                        ("top_logprobs", top_logprobs),
                        ("top_p", top_p),
                        ("user", user),
                    )
                    if v is not None and v is not NOT_GIVEN and v is not GroqNotGiven
                }
            )
        )
        stream_chat_chunks = self._client.groq_client.chat.completions.create(
            messages=messages, model=model, stream=True, **params  # type: ignore
        )

        # Get the message stream
        httpx_response_stream = ResponseStream(
            self.generator_generate_content_chunks(stream_chat_chunks)
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
        stream_chat_completion_chunks: "GroqStream[GroqChatCompletionChunk]",
        *,
        encoding: Text = "utf-8",
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

        # Generate the chat response
        for chunk in stream_chat_completion_chunks:
            openai_chunk = ChatCompletionChunk.model_validate(
                chunk.model_dump(exclude_none=True)
            )
            yield simple_encode_sse(openai_chunk, encoding=encoding)

        # End the stream
        yield simple_encode_sse("[DONE]", encoding=encoding)


class GroqChat(OpenAIResources.Chat):
    @cached_property
    def completions(self) -> GroqChatCompletions:
        return GroqChatCompletions(self._client)


class GroqModels(OpenAIResources.Models):

    _client: "GroqOpenAI"

    supported_models = frozenset(MODELS_GROQ)

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
        try:
            retrieved_model = self._client.groq_client.models.retrieve(model=model)
        except GroqNotFoundError as e:
            raise openai.NotFoundError(
                str(e),
                response=httpx.Response(status_code=404, text=str(e)),
                body=None,
            )
        return Model.model_validate(
            {
                "id": retrieved_model.id,
                "created": retrieved_model.created,
                "object": "model",
                "owned_by": "groq",
            }
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
        model_list_res = self._client.groq_client.models.list()
        models = [
            Model.model_validate(
                {
                    "id": model.id,
                    "created": model.created,
                    "object": "model",
                    "owned_by": "groq",
                }
            )
            for model in model_list_res.data
        ]
        return SyncPage(data=models, object="list")


class GroqOpenAI(OpenAI):
    chat: GroqChat
    models: GroqModels

    groq_client: Groq

    def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
        api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise CredentialsNotProvided("Groq API key is not provided")
        kwargs["api_key"] = api_key
        kwargs = {k: v for k, v in kwargs.items() if k in openai_init_parameter_keys}

        super().__init__(**kwargs)

        self.chat = GroqChat(self)
        self.models = GroqModels(self)

        self.groq_client = Groq(api_key=api_key)
