import math
import random
import time
from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai.types.completion import Completion
from pyassorted.asyncio.executor import run_func, run_generator

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.deps.common import app_settings
from languru.server.utils.common import get_value_from_app
from languru.types.completions import CompletionRequest
from languru.utils.http import simple_sse_encode

if TYPE_CHECKING:
    from openai import Stream

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
        from openai import OpenAI

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

        # Request completion
        client = OpenAI(base_url=model.owned_by, api_key="NOT_IMPLEMENTED")
        # Stream
        if completion_request.stream is True:
            completion_stream_params = completion_request.model_dump(exclude_none=True)
            completion_stream_params.pop("stream", None)
            text_completion_stream: "Stream[Completion]" = await run_func(
                client.completions.create, **completion_stream_params, stream=True
            )
            return StreamingResponse(
                simple_sse_encode(text_completion_stream, logger=settings.APP_NAME),
                media_type="application/stream+json",
            )
        # Normal
        else:
            return await run_func(
                client.completions.create,
                completion_request.model_dump(exclude_none=True),
            )


@router.post("/completions")
async def text_completions(
    request: Request,
    completion_request: CompletionRequest = Body(
        ...,
        openapi_examples={
            "Quick text completion": {
                "summary": "Quick text completion",
                "description": "Text completion request",
                "value": {
                    "model": "gpt-3.5-turbo-instruct",
                    "prompt": "Say this is a test",
                    "max_tokens": 7,
                    "temperature": 0,
                },
            },
        },
    ),
    settings: ServerBaseSettings = Depends(app_settings),
):  # openai.types.Completion
    return await TextCompletionHandler().handle_request(
        request=request,
        completion_request=completion_request,
        settings=settings,
    )
