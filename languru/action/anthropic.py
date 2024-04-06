import os
import time
from typing import TYPE_CHECKING, Generator, List, Optional, Text

import anthropic
from anthropic.types.message_param import MessageParam as MessageParamDict
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from languru.action.base import ActionBase, ModelDeploy
from languru.config import logger
from languru.types.chat.anthropic import AnthropicChatCompletionRequest
from languru.types.chat.completions import ChatCompletionRequest

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


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
        # Validate model name
        model = self.validate_model(model)
        # Prepare request
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

        # Send request
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

    def chat_stream(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator["ChatCompletionChunk", None, None]:
        # Validate stream
        if "stream" in kwargs and not kwargs["stream"]:
            logger.warning(f"Chat stream should be True, but got: {kwargs['stream']}")
        # Validate model name
        model = self.validate_model(model)
        # Prepare request
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

        # Send request
        msg_id = None
        model_name = anthropic_req.model
        input_tokens = 0
        finish_reason = "stop"
        role = "assistant"
        res_stream = self.client.messages.create(
            max_tokens=anthropic_req.max_tokens,
            messages=[
                MessageParamDict(**m.model_dump()) for m in anthropic_req.messages
            ],
            model=anthropic_req.model,
            stream=True,
            **anthropic_req.model_dump(
                exclude_none=True, exclude={"max_tokens", "messages", "model", "stream"}
            ),
        )
        for message_event in res_stream:
            if message_event.type == "message_start":
                msg_id = message_event.message.id
                model_name = message_event.message.model
                input_tokens = message_event.message.usage.input_tokens  # noqa: F841
                role = message_event.message.role
            if message_event.type == "message_delta":
                output_tokens = message_event.usage.output_tokens  # noqa: F841
                if message_event.delta.stop_reason == "end_turn":
                    finish_reason = "stop"
                elif message_event.delta.stop_reason == "max_tokens":
                    finish_reason = "length"
                elif message_event.delta.stop_reason == "stop_sequence":
                    finish_reason = "stop"
                else:
                    logger.warning(
                        f"Unknown stop reason: {message_event.delta.stop_reason}"
                    )
            if message_event.type == "content_block_delta":
                yield ChatCompletionChunk.model_validate(
                    {
                        "id": msg_id,
                        "choices": [
                            {
                                "delta": {
                                    "content": message_event.delta.text,
                                    "role": role,
                                },
                                "index": 0,
                            }
                        ],
                        "created": int(time.time()),
                        "model": model_name,
                        "object": "chat.completion.chunk",
                    }
                )
        # logger.debug(f"Total tokens: {input_tokens + output_tokens}")
        yield ChatCompletionChunk.model_validate(
            {
                "id": msg_id,
                "choices": [
                    {
                        "finish_reason": finish_reason,
                        "delta": {"content": "", "role": role},
                        "index": 0,
                    }
                ],
                "created": int(time.time()),
                "model": model_name,
                "object": "chat.completion.chunk",
            }
        )
