import math
import random
import time
from typing import cast

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from openai.types import ModerationCreateResponse
from pyassorted.asyncio.executor import run_func

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.deps.common import app_settings
from languru.server.utils.common import get_value_from_app
from languru.types.moderations import ModerationRequest

router = APIRouter()


class ModerationsHandler:
    async def handle_moderations_request(
        self,
        request: "Request",
        moderation_request: "ModerationRequest",
        settings: "ServerBaseSettings",
    ) -> "ModerationCreateResponse":
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_moderations_llm(
                request=request,
                moderation_request=moderation_request,
                settings=settings,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_moderations_agent(
                request=request,
                moderation_request=moderation_request,
                settings=settings,
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

    async def handle_moderations_llm(
        self,
        request: "Request",
        moderation_request: "ModerationRequest",
        settings: "LlmSettings",
    ) -> "ModerationCreateResponse":
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )
        try:
            moderation_request.model = action.get_model_name(moderation_request.model)
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        moderation = await run_func(
            action.moderations, **moderation_request.model_dump(exclude_none=True)
        )
        return moderation

    async def handle_moderations_agent(
        self,
        request: "Request",
        moderation_request: "ModerationRequest",
        settings: "AgentSettings",
    ) -> "ModerationCreateResponse":
        from openai import OpenAI

        from languru.resources.model.discovery import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        models = await run_func(
            model_discovery.list,
            id=moderation_request.model,
            created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
        )
        if len(models) == 0:
            raise HTTPException(
                status_code=404, detail=f"Model '{moderation_request.model}' not found"
            )

        model = random.choice(models)
        client = OpenAI(base_url=model.owned_by, api_key="NOT_IMPLEMENTED")
        return await run_func(
            client.moderations.create,
            **moderation_request.model_dump(exclude_none=True),
        )


@router.post("/moderations")
async def request_moderations(
    request: Request,
    moderation_request: ModerationRequest = Body(
        ...,
        openapi_examples={
            "Quick example": {
                "summary": "A quick example of a moderation request",
                "description": "A quick example of a moderation request",
                "value": {"input": "I want to kill them."},
            }
        },
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ModerationCreateResponse:
    return await ModerationsHandler().handle_moderations_request(
        request=request, moderation_request=moderation_request, settings=settings
    )
