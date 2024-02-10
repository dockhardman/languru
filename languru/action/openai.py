from typing import TYPE_CHECKING, List, Optional, Text

import openai

from languru.action.base import ActionBase, ModelDeploy
from languru.llm.config import logger

if TYPE_CHECKING:
    from openai.types import (
        Completion,
        CreateEmbeddingResponse,
        ModerationCreateResponse,
    )
    from openai.types.chat import ChatCompletion, ChatCompletionMessageParam


class OpenaiAction(ActionBase):
    model_deploys = (
        ModelDeploy("babbage-002", "babbage-002"),
        ModelDeploy("dall-e-2", "dall-e-2"),
        ModelDeploy("dall-e-3", "dall-e-3"),
        ModelDeploy("davinci-002", "davinci-002"),
        ModelDeploy("gpt-3.5-turbo", "gpt-3.5-turbo"),
        ModelDeploy("gpt-3.5-turbo-0125", "gpt-3.5-turbo-0125"),
        ModelDeploy("gpt-3.5-turbo-0301", "gpt-3.5-turbo-0301"),
        ModelDeploy("gpt-3.5-turbo-0613", "gpt-3.5-turbo-0613"),
        ModelDeploy("gpt-3.5-turbo-1106", "gpt-3.5-turbo-1106"),
        ModelDeploy("gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k"),
        ModelDeploy("gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k-0613"),
        ModelDeploy("gpt-3.5-turbo-instruct", "gpt-3.5-turbo-instruct"),
        ModelDeploy("gpt-3.5-turbo-instruct-0914", "gpt-3.5-turbo-instruct-0914"),
        ModelDeploy("gpt-4", "gpt-4"),
        ModelDeploy("gpt-4-0125-preview", "gpt-4-0125-preview"),
        ModelDeploy("gpt-4-0613", "gpt-4-0613"),
        ModelDeploy("gpt-4-1106-preview", "gpt-4-1106-preview"),
        ModelDeploy("gpt-4-turbo-preview", "gpt-4-turbo-preview"),
        ModelDeploy("gpt-4-vision-preview", "gpt-4-vision-preview"),
        ModelDeploy("text-embedding-3-large", "text-embedding-3-large"),
        ModelDeploy("text-embedding-3-small", "text-embedding-3-small"),
        ModelDeploy("text-embedding-ada-002", "text-embedding-ada-002"),
        ModelDeploy("text-moderation-latest", "text-moderation-latest"),
        ModelDeploy("text-moderation-stable", "text-moderation-stable"),
        ModelDeploy("tts-1", "tts-1"),
        ModelDeploy("tts-1-1106", "tts-1-1106"),
        ModelDeploy("tts-1-hd", "tts-1-hd"),
        ModelDeploy("tts-1-hd-1106", "tts-1-hd-1106"),
        ModelDeploy("whisper-1", "whisper-1"),
    )

    def __init__(
        self,
        *args,
        api_key: Optional[Text] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._client = openai.OpenAI(api_key=api_key)

    def name(self):
        return "openai_action"

    def health(self) -> bool:
        try:
            self._client.models.retrieve(model="gpt-3.5-turbo")
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

    def chat(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> "ChatCompletion":
        chat_completion = self._client.chat.completions.create(
            messages=messages, model=model, **kwargs
        )
        return chat_completion

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        completion = self._client.completions.create(
            prompt=prompt, model=model, **kwargs
        )
        return completion

    def embeddings(
        self, input: Text, *args, model: Text, **kwargs
    ) -> "CreateEmbeddingResponse":
        embeddings = self._client.embeddings.create(input=input, model=model, **kwargs)
        return embeddings

    def moderations(
        self, input: Text, *args, model: Text, **kwargs
    ) -> "ModerationCreateResponse":
        moderation = self._client.moderations.create(input=input, model=model, **kwargs)
        return moderation
