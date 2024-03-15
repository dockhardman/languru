import math
import random
import time
from typing import cast

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pyassorted.asyncio.executor import run_func, run_generator
from yarl import URL

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.deps.common import app_settings
from languru.server.utils.common import get_value_from_app
from languru.types.chat.completions import ChatCompletionRequest
from languru.utils.http import requests_stream_lines

router = APIRouter()


class ChatCompletionHandler:

    async def handle_request(
        self,
        request: "Request",
        chat_completion_request: "ChatCompletionRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ChatCompletion | ChatCompletionChunk | StreamingResponse:
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_llm(
                request=request,
                chat_completion_request=chat_completion_request,
                settings=settings,
                **kwargs,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_agent(
                request=request,
                chat_completion_request=chat_completion_request,
                settings=settings,
                **kwargs,
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_llm(
        self,
        request: "Request",
        chat_completion_request: "ChatCompletionRequest",
        settings: "LlmSettings",
        **kwargs,
    ) -> ChatCompletion | ChatCompletionChunk | StreamingResponse:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )

        try:
            chat_completion_request.model = action.get_model_name(
                chat_completion_request.model
            )
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Stream
        if chat_completion_request.stream is True:
            return StreamingResponse(
                run_generator(
                    action.chat_stream_sse,
                    **chat_completion_request.model_dump(exclude_none=True),
                ),
                media_type="application/stream+json",
            )

        # Normal
        else:
            chat_completion = await run_func(
                action.chat, **chat_completion_request.model_dump(exclude_none=True)
            )
            return chat_completion

    async def handle_agent(
        self,
        request: "Request",
        chat_completion_request: "ChatCompletionRequest",
        settings: "AgentSettings",
        **kwargs,
    ) -> ChatCompletion | ChatCompletionChunk | StreamingResponse:
        from languru.resources.model.discovery import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )

        # Get model name and model destination
        models = await run_func(
            model_discovery.list,
            id=chat_completion_request.model,
            created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
        )
        if len(models) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{chat_completion_request.model}' not found",
            )
        model = random.choice(models)
        url = URL(model.owned_by).with_path("/chat/completions")

        # Request completion
        # Stream
        if chat_completion_request.stream is True:
            return StreamingResponse(
                requests_stream_lines(
                    str(url),
                    data=chat_completion_request.model_dump(exclude_none=True),
                ),
                media_type="application/stream+json",
            )
        # Normal
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    str(url),
                    json=chat_completion_request.model_dump(exclude_none=True),
                )
                response.raise_for_status()
                return ChatCompletion(**response.json())


chat_completion_handler = ChatCompletionHandler()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    chat_completion_request: ChatCompletionRequest = Body(
        ...,
        example={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        },
    ),
    settings: ServerBaseSettings = Depends(app_settings),
):  # -> openai.types.chat.ChatCompletion | openai.types.chat.ChatCompletionChunk
    return await chat_completion_handler.handle_request(
        request=request,
        chat_completion_request=chat_completion_request,
        settings=settings,
    )
