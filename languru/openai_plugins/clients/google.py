import os
import time
import uuid
from typing import Dict, Generator, Iterable, List, Literal, Optional, Text, Union

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
from openai.types.create_embedding_response import CreateEmbeddingResponse
from openai.types.model import Model

from languru.exceptions import CredentialsNotProvided
from languru.openai_plugins.clients.utils import openai_init_parameter_keys
from languru.types.models import MODELS_GOOGLE
from languru.utils.openai_utils import rand_chat_completion_id
from languru.utils.sse import simple_encode_sse


class GoogleChatCompletions(Completions):
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

        # pop out the last message
        genai_model = genai.GenerativeModel(model)
        contents: List[ContentDict] = [
            ContentDict(
                role=(
                    "model" if m["role"] == "assistant" else "user"
                ),  # Gemini roles: user, model
                parts=[m["content"]],
            )
            for m in messages
            if "content" in m and m["content"]
        ]
        input_tokens = genai_model.count_tokens(contents).total_tokens

        # Generate the chat response
        latest_content = contents.pop()
        chat_session = genai_model.start_chat(history=contents or None)
        send_message_kwargs = dict()
        if temperature is not None and not isinstance(temperature, NotGiven):
            send_message_kwargs["generation_config"] = (
                generation_types.GenerationConfigDict(temperature=temperature)
            )
        response = chat_session.send_message(latest_content, **send_message_kwargs)
        out_tokens = genai_model.count_tokens(response.parts).total_tokens

        # Parse the response
        chat_completion = ChatCompletion.model_validate(
            dict(
                id=str(uuid.uuid4()),
                choices=[
                    dict(
                        finish_reason="stop",
                        index=idx,
                        message=dict(content=part.text, role="assistant"),
                    )
                    for idx, part in enumerate(response.parts)
                    if part.text
                ],
                created=int(time.time()),
                model=model,
                object="chat.completion",
                usage=dict(
                    completion_tokens=out_tokens,
                    prompt_tokens=input_tokens,
                    total_tokens=input_tokens + out_tokens,
                ),
            )
        )
        return chat_completion

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

        # pop out the last message
        genai_model = genai.GenerativeModel(model)
        contents: List[ContentDict] = [
            ContentDict(
                role=(
                    "model" if m["role"] == "assistant" else "user"
                ),  # Gemini roles: user, model
                parts=[m["content"]],
            )
            for m in messages
            if "content" in m and m["content"]
        ]

        # Generate the chat response
        latest_content = contents.pop()
        chat_session = genai_model.start_chat(history=contents or None)
        send_message_kwargs = dict()
        if temperature is not None and not isinstance(temperature, NotGiven):
            send_message_kwargs["generation_config"] = (
                generation_types.GenerationConfigDict(temperature=temperature)
            )
        send_message_kwargs["stream"] = True
        genai_response = chat_session.send_message(
            latest_content, **send_message_kwargs
        )
        httpx_response_stream = ResponseStream(
            self.generator_generate_content_chunks(genai_response, model=model)
        )
        httpx_response = httpx.Response(
            status_code=200,
            headers={"content-type": "text/plain"},
            stream=httpx_response_stream,
        )
        return Stream(
            cast_to=ChatCompletionChunk, response=httpx_response, client=self._client
        )

    def generator_generate_content_chunks(
        self,
        generate_content_response: "generation_types.GenerateContentResponse",
        *,
        model: Text,
        encoding: Text = "utf-8",
        created: Optional[int] = None,
        chat_completion_id: Optional[Text] = None,
    ) -> Generator[bytes, None, None]:
        """Generate the chat completion response in chunks.

        Parameters
        ----------
        generate_content_response : generation_types.GenerateContentResponse
            The response from the GenAI model.
        model : Text
            The model name.
        encoding : Text, optional
            The encoding format, by default "utf-8".
        created : Optional[int], optional
            The timestamp when the chat completion was created, by default None.
        chat_completion_id : Optional[Text], optional
            The chat completion ID, by default None.

        Yields
        ------
        Generator[bytes, None, None]
            The chat completion response in chunks.
        """

        chat_completion_id = chat_completion_id or rand_chat_completion_id()
        created = created or int(time.time())

        # Generate the chat response
        for generate_content_chunk in generate_content_response:
            parts_content = "\n".join(
                p.text for p in generate_content_chunk.candidates[0].content.parts
            )
            chunk = ChatCompletionChunk.model_validate(
                {
                    "id": chat_completion_id,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": parts_content, "role": "assistant"},
                        }
                    ],
                    "created": created,
                    "model": model,
                    "object": "chat.completion.chunk",
                }
            )
            yield simple_encode_sse(chunk, encoding=encoding)

        # Send the final chunk with finish_reason
        chunk = ChatCompletionChunk.model_validate(
            {
                "id": chat_completion_id,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                "created": created,
                "model": model,
                "object": "chat.completion.chunk",
            }
        )
        yield simple_encode_sse(chunk, encoding=encoding)

        # End the stream
        yield simple_encode_sse("[DONE]", encoding=encoding)


class GoogleChat(OpenAIResources.Chat):
    @cached_property
    def completions(self) -> GoogleChatCompletions:
        return GoogleChatCompletions(self._client)


class GoogleModels(OpenAIResources.Models):

    supported_models = frozenset(MODELS_GOOGLE)

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
            google_model = genai.get_model(model)
        except GoogleNotFound as e:
            error_message = str(e)
            raise openai.NotFoundError(
                error_message,
                response=httpx.Response(status_code=404, text=error_message),
                body=None,
            ) from e
        return Model.model_validate(
            {
                "id": google_model.name,
                "created": int(time.time()),
                "object": "model",
                "owned_by": "google",
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
        models = [
            Model.model_validate(
                {
                    "id": model.name,
                    "created": int(time.time()),
                    "object": "model",
                    "owned_by": "google",
                }
            )
            for model in list(genai.list_models())
        ]
        return SyncPage(data=models, object="list")


class GoogleEmbeddings(OpenAIResources.Embeddings):
    def create(
        self,
        *,
        input: Union[str, List[str], Iterable[int], Iterable[Iterable[int]]],
        model: Text,
        dimensions: int | NotGiven = NOT_GIVEN,
        encoding_format: Literal["float", "base64"] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateEmbeddingResponse:
        input = [input] if isinstance(input, Text) else input
        embedding_res = genai.embed_content(model=model, content=input)
        embeddings: List[List[float]] = embedding_res.get("embedding", [])
        return CreateEmbeddingResponse.model_validate(
            {
                "data": [
                    {
                        "embedding": emb,
                        "index": idx,
                        "object": "embedding",
                    }
                    for idx, emb in enumerate(embeddings)
                ],
                "model": model,
                "object": "list",
                "usage": {
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            }
        )


class GoogleOpenAI(OpenAI):
    chat: GoogleChat
    models: GoogleModels
    embeddings: GoogleEmbeddings

    def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
        api_key = (
            api_key
            or os.getenv("GOOGLE_GENAI_API_KEY")
            or os.getenv("GOOGLE_AI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            raise CredentialsNotProvided("Google GenAI API key is not provided")
        kwargs["api_key"] = api_key
        kwargs = {k: v for k, v in kwargs.items() if k in openai_init_parameter_keys}

        super().__init__(**kwargs)

        genai.configure(api_key=api_key)

        self.chat = GoogleChat(self)
        self.models = GoogleModels(self)
        self.embeddings = GoogleEmbeddings(self)
