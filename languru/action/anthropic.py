import os
import time
from typing import TYPE_CHECKING, Generator, List, Optional, Text

import anthropic
from anthropic.types.message_param import MessageParam as MessageParamDict
from openai.types.chat import ChatCompletion

from languru.action.base import ActionBase, ModelDeploy
from languru.config import logger
from languru.types.chat.anthropic import AnthropicChatCompletionRequest
from languru.types.chat.completions import ChatCompletionRequest

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam


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
        chat_req = ChatCompletionRequest.from_kwargs(
            messages=messages, model=model, **kwargs
        )
        anthropic_req = (
            AnthropicChatCompletionRequest.from_openai_chat_completion_request(chat_req)
        )
        if anthropic_req.stream is True:
            logger.warning(
                f"Chat stream should be False, but got: {anthropic_req.stream}"
            )
        res_message = self.client.messages.create(
            max_tokens=anthropic_req.max_tokens,
            messages=[
                MessageParamDict(**m.model_dump()) for m in anthropic_req.messages
            ],
            model=anthropic_req.model,
            stream=False,
            **anthropic_req.model_dump(
                exclude_none=True, exclude={"max_tokens", "messages", "model", "stream"}
            ),
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

    def chat_stream(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator["ChatCompletionChunk", None, None]:
        if "stream" in kwargs and not kwargs["stream"]:
            logger.warning(f"Chat stream should be True, but got: {kwargs['stream']}")
        model = self.validate_model(model)
