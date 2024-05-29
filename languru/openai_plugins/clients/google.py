import os
from typing import Dict, Iterable, List, Literal, Optional, Text, Union

import google.generativeai as genai
import httpx
from openai import OpenAI
from openai import resources as OpenAIResources
from openai._compat import cached_property
from openai._streaming import Stream
from openai._types import NOT_GIVEN, Body, Headers, NotGiven, Query
from openai._utils import required_args
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

from languru.config import logger
from languru.openai_plugins.clients.utils import openai_init_parameter_keys


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
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        pass


class GoogleChat(OpenAIResources.Chat):
    @cached_property
    def completions(self) -> Completions:
        return Completions(self._client)


class GoogleOpenAI(OpenAI):
    chat: GoogleChat

    def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
        api_key = (
            api_key
            or os.getenv("GOOGLE_GENAI_API_KEY")
            or os.getenv("GOOGLE_AI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not api_key:
            logger.error("Google GenAI API key is not provided")
        kwargs["api_key"] = api_key
        kwargs = {k: v for k, v in kwargs.items() if k in openai_init_parameter_keys}

        super().__init__(**kwargs)

        self.chat = GoogleChat(self)

        genai.configure(api_key=api_key)
