from typing import TYPE_CHECKING

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import StreamingResponse
from openai.types.chat import ChatCompletion
from pyassorted.asyncio.executor import run_func, run_generator

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.chat.completions import ChatCompletionRequest
from languru.utils.http import simple_sse_encode

if TYPE_CHECKING:
    from openai import OpenAI

router = APIRouter()


class ChatCompletionHandler:

    async def handle_request(
        self,
        request: "Request",
        *args,
        chat_completion_request: "ChatCompletionRequest",
        settings: "ServerBaseSettings",
        openai_client: "OpenAI",
        **kwargs,
    ) -> ChatCompletion | StreamingResponse:
        if chat_completion_request.stream is True:
            return await self.handle_stream(
                request=request,
                chat_completion_request=chat_completion_request,
                settings=settings,
                openai_client=openai_client,
                **kwargs,
            )
        else:
            return await self.handle_normal(
                request=request,
                chat_completion_request=chat_completion_request,
                settings=settings,
                openai_client=openai_client,
                **kwargs,
            )

    async def handle_normal(
        self,
        request: "Request",
        *args,
        chat_completion_request: "ChatCompletionRequest",
        settings: "ServerBaseSettings",
        openai_client: "OpenAI",
        **kwargs,
    ) -> ChatCompletion:
        params = chat_completion_request.model_dump(exclude_none=True)
        params["stream"] = False
        chat_completion = await run_func(
            openai_client.chat.completions.create, **params
        )
        return chat_completion

    async def handle_stream(
        self,
        request: "Request",
        *args,
        chat_completion_request: "ChatCompletionRequest",
        settings: "ServerBaseSettings",
        openai_client: "OpenAI",
        **kwargs,
    ) -> StreamingResponse:
        params = chat_completion_request.model_dump(exclude_none=True)
        params["stream"] = True
        return StreamingResponse(
            run_generator(
                simple_sse_encode(
                    await run_func(
                        openai_client.chat.completions.create, **params
                    ),  # type: ignore
                )
            ),
            media_type="application/stream+json",
        )


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    chat_completion_request: ChatCompletionRequest = Body(
        ...,
        openapi_examples={
            "OpenAI": {
                "summary": "OpenAI",
                "description": "Chat completion request",
                "value": {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hello!"},
                    ],
                },
            },
            "Google Gemini": {
                "summary": "Google Gemini",
                "description": "Chat completion request",
                "value": {
                    "model": "gemini-pro",
                    "messages": [{"role": "user", "content": "Hello, how are you?"}],
                },
            },
            "Perplexity Sonar": {
                "summary": "Perplexity Sonar",
                "description": "Chat completion request",
                "value": {
                    "model": "sonar-small-chat",
                    "messages": [
                        {"role": "system", "content": "Be precise and concise."},
                        {
                            "role": "user",
                            "content": "How many stars are there in our galaxy?",
                        },
                    ],
                },
            },
            "Groq Mixtral": {
                "summary": "Groq Mixtral",
                "description": "Chat completion request",
                "value": {
                    "model": "sonar-small-chat",
                    "messages": [
                        {"role": "system", "content": "You are an unhelpful assistant"},
                        {"role": "user", "content": "Are you a fish?"},
                    ],
                },
            },
        },
    ),
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
):  # -> openai.types.chat.ChatCompletion | openai.types.chat.ChatCompletionChunk
    return await ChatCompletionHandler().handle_request(
        request=request,
        chat_completion_request=chat_completion_request,
        settings=settings,
        openai_client=openai_client,
    )
