import os
from typing import TYPE_CHECKING, Generator, List, Optional, Text, Union

import anthropic

from languru.action.base import ActionBase, ModelDeploy
from languru.config import logger

if TYPE_CHECKING:
    from openai.types import (
        Completion,
        CreateEmbeddingResponse,
        ModerationCreateResponse,
    )
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionMessageParam,
    )


class AnthropicAction(ActionBase):
    model_deploys = (
        ModelDeploy("anthropic/claude-2.0", "claude-2.0"),
        ModelDeploy("anthropic/claude-2.1", "claude-2.1"),
        ModelDeploy("anthropic/claude-3-haiku", "claude-3-haiku-20240307"),
        ModelDeploy("anthropic/claude-3-haiku-20240307", "claude-3-haiku-20240307"),
        ModelDeploy("anthropic/claude-3-opus", "claude-3-opus-20240229"),
        ModelDeploy("anthropic/claude-3-opus-20240229", "claude-3-opus-20240229"),
        ModelDeploy("anthropic/claude-3-sonnet", "claude-3-sonnet-20240229"),
        ModelDeploy("anthropic/claude-3-sonnet-20240229", "claude-3-sonnet-20240229"),
        ModelDeploy("anthropic/claude-instant-1.2", "claude-instant-1.2"),
        ModelDeploy("claude-2.0", "claude-2.0"),
        ModelDeploy("claude-2.1", "claude-2.1"),
        ModelDeploy("claude-3-haiku", "claude-3-haiku-20240307"),
        ModelDeploy("claude-3-haiku-20240307", "claude-3-haiku-20240307"),
        ModelDeploy("claude-3-opus", "claude-3-opus-20240229"),
        ModelDeploy("claude-3-opus-20240229", "claude-3-opus-20240229"),
        ModelDeploy("claude-3-sonnet", "claude-3-sonnet-20240229"),
        ModelDeploy("claude-3-sonnet-20240229", "claude-3-sonnet-20240229"),
        ModelDeploy("claude-instant-1.2", "claude-instant-1.2"),
    )

    def __init__(
        self,
        *args,
        api_key: Optional[Text] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        __api_key = (
            api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("API_KEY")
        )
        if __api_key is None:
            raise ValueError("API key is required for Anthropic API")
        self.client = anthropic.Anthropic(api_key=__api_key)

    def name(self):
        return "anthropic_action"

    def health(self) -> bool:
        try:
            self.client.count_tokens(text="Health check")
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False

    def chat(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> "ChatCompletion":
        model = self.validate_model(model)

    def chat_stream(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator["ChatCompletionChunk", None, None]:
        if "stream" in kwargs and not kwargs["stream"]:
            logger.warning(f"Chat stream should be True, but got: {kwargs['stream']}")
        model = self.validate_model(model)

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        model = self.validate_model(model)

    def text_completion_stream(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> Generator["Completion", None, None]:
        if "stream" in kwargs and not kwargs["stream"]:
            logger.warning(
                f"Text completion stream should be True, but got: {kwargs['stream']}"
            )
        kwargs.pop("stream", None)
        model = self.validate_model(model)
