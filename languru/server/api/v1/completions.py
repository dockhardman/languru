import math
import random
import time
from typing import cast

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai.types.completion import Completion
from pyassorted.asyncio.executor import run_func, run_generator
from yarl import URL

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.utils.common import get_value_from_app
from languru.types.completions import CompletionRequest
from languru.utils.http import requests_stream_lines

router = APIRouter()


class TextCompletionHandler:

    async def handle_request(
        self,
        request: "Request",
        completion_request: "CompletionRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> Completion | StreamingResponse:
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_llm(
                request=request,
                completion_request=completion_request,
                settings=settings,
                **kwargs,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_agent(
                request=request,
                completion_request=completion_request,
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
        completion_request: "CompletionRequest",
        settings: "LlmSettings",
        **kwargs,
    ) -> Completion | StreamingResponse:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )

        try:
            completion_request.model = action.get_model_name(completion_request.model)
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Stream
        if completion_request.stream is True:
            return StreamingResponse(
                run_generator(
                    action.text_completion_stream_sse,
                    **completion_request.model_dump(exclude_none=True),
                ),
                media_type="application/stream+json",
            )
        # Normal
        else:
            completion = await run_func(
                action.text_completion,
                **completion_request.model_dump(exclude_none=True),
            )
            return completion

    async def handle_agent(
        self,
        request: "Request",
        completion_request: "CompletionRequest",
        settings: "AgentSettings",
        **kwargs,
    ) -> Completion | StreamingResponse:
        from languru.resources.model.discovery import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        models = await run_func(
            model_discovery.list,
            id=completion_request.model,
            created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
        )
        if len(models) == 0:
            raise HTTPException(
                status_code=404, detail=f"Model '{completion_request.model}' not found"
            )

        model = random.choice(models)
        url = URL(model.owned_by).with_path("/completions")
        # Request completion
        # Stream
        if completion_request.stream is True:
            return StreamingResponse(
                requests_stream_lines(
                    str(url), data=completion_request.model_dump(exclude_none=True)
                ),
                media_type="application/stream+json",
            )
        # Normal
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    str(url), json=completion_request.model_dump(exclude_none=True)
                )
                response.raise_for_status()
                return Completion(**response.json())


text_completion_handler = TextCompletionHandler()


@router.post("/completions")
async def text_completions(
    request: Request,
    completion_request: CompletionRequest = Body(
        ...,
        example={
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
        },
    ),
):  # openai.types.Completion
    return await text_completion_handler.handle_request(
        request=request,
        completion_request=completion_request,
        settings=get_value_from_app(
            request.app, key="settings", value_typing=ServerBaseSettings
        ),
    )
