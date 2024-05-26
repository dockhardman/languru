import logging
import math
import random
import time
from typing import Text, cast

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from openai.types import ImagesResponse
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
from languru.types.images import (
    ImagesEditRequest,
    ImagesGenerationsRequest,
    ImagesVariationsRequest,
)

router = APIRouter()


class ImagesGenerationsHandler:
    async def handle_request(
        self,
        request: "Request",
        images_generations_request: "ImagesGenerationsRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ImagesResponse:
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_llm(
                request=request,
                images_generations_request=images_generations_request,
                settings=settings,
                **kwargs,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_agent(
                request=request,
                images_generations_request=images_generations_request,
                settings=settings,
                **kwargs,
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_llm(
        self,
        request: "Request",
        images_generations_request: "ImagesGenerationsRequest",
        settings: "LlmSettings",
        **kwargs,
    ) -> ImagesResponse:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )
        try:
            images_generations_request.model = action.get_model_name(
                images_generations_request.model
            )
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        else:
            image_res = await run_func(
                action.images_generations,
                **images_generations_request.model_dump(exclude_none=True),
            )
            return image_res

    async def handle_agent(
        self,
        request: "Request",
        images_generations_request: "ImagesGenerationsRequest",
        settings: "AgentSettings",
        **kwargs,
    ) -> ImagesResponse:
        from openai import OpenAI

        from languru.resources.model_discovery.base import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        logger = logging.getLogger(settings.APP_NAME)

        # Get model name and model destination
        models = await run_func(
            model_discovery.list,
            id=images_generations_request.model,
            created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
        )
        if len(models) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{images_generations_request.model}' not found",
            )
        model = random.choice(models)

        # Request audio speech
        client = OpenAI(base_url=model.owned_by, api_key="NOT_IMPLEMENTED")
        logger.debug(f"Using model '{model.id}' from '{model.owned_by}'")
        return await run_func(
            client.images.generate,
            **images_generations_request.model_dump(exclude_none=True),
        )


class ImagesEditsHandler:
    async def handle_request(
        self,
        request: "Request",
        images_edit_request: "ImagesEditRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ImagesResponse:
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_llm(
                request=request,
                images_edit_request=images_edit_request,
                settings=settings,
                **kwargs,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_agent(
                request=request,
                images_edit_request=images_edit_request,
                settings=settings,
                **kwargs,
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_llm(
        self,
        request: "Request",
        images_edit_request: "ImagesEditRequest",
        settings: "LlmSettings",
        **kwargs,
    ) -> ImagesResponse:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )
        image_res = await run_func(
            action.images_edits, **images_edit_request.model_dump(exclude_none=True)
        )
        return image_res

    async def handle_agent(
        self,
        request: "Request",
        images_edit_request: "ImagesEditRequest",
        settings: "AgentSettings",
        **kwargs,
    ) -> ImagesResponse:
        from openai import OpenAI

        from languru.resources.model_discovery.base import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        logger = logging.getLogger(settings.APP_NAME)

        # Get model name and model destination
        models = await run_func(
            model_discovery.list,
            id=images_edit_request.model,
            created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
        )
        if len(models) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{images_edit_request.model}' not found",
            )
        model = random.choice(models)

        # Request audio speech
        client = OpenAI(base_url=model.owned_by, api_key="NOT_IMPLEMENTED")
        logger.debug(f"Using model '{model.id}' from '{model.owned_by}'")
        return await run_func(
            client.images.edit,
            **images_edit_request.model_dump(exclude_none=True),
        )


class ImagesVariationsHandler:
    async def handle_request(
        self,
        request: "Request",
        images_variations_request: "ImagesVariationsRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ImagesResponse:
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_llm(
                request=request,
                images_variations_request=images_variations_request,
                settings=settings,
                **kwargs,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_agent(
                request=request,
                images_variations_request=images_variations_request,
                settings=settings,
                **kwargs,
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_llm(
        self,
        request: "Request",
        images_variations_request: "ImagesVariationsRequest",
        settings: "LlmSettings",
        **kwargs,
    ) -> ImagesResponse:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )
        image_res = await run_func(
            action.images_variations,
            **images_variations_request.model_dump(exclude_none=True),
        )
        return image_res

    async def handle_agent(
        self,
        request: "Request",
        images_variations_request: "ImagesVariationsRequest",
        settings: "AgentSettings",
        **kwargs,
    ) -> ImagesResponse:
        from openai import OpenAI

        from languru.resources.model_discovery.base import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        logger = logging.getLogger(settings.APP_NAME)

        # Get model name and model destination
        models = await run_func(
            model_discovery.list,
            id=images_variations_request.model,
            created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
        )
        if len(models) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{images_variations_request.model}' not found",
            )
        model = random.choice(models)

        # Request audio speech
        client = OpenAI(base_url=model.owned_by, api_key="NOT_IMPLEMENTED")
        logger.debug(f"Using model '{model.id}' from '{model.owned_by}'")
        return await run_func(
            client.images.create_variation,
            **images_variations_request.model_dump(exclude_none=True),
        )


@router.post("/images/generations")
async def images_generations(
    request: Request,
    images_generations_request: ImagesGenerationsRequest = Body(
        ...,
        openapi_examples={
            "OpenAI": {
                "summary": "OpenAI",
                "description": "Generate images using OpenAI's DALL-E model.",
                "value": {
                    "prompt": "A cute baby sea otter",
                    "model": "dall-e-2",
                    "size": "256x256",
                },
            },
        },
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesGenerationsHandler().handle_request(
        request=request,
        images_generations_request=images_generations_request,
        settings=settings,
    )


@router.post("/images/edits")
async def images_edits(
    request: Request,
    image: UploadFile = File(...),
    prompt: Text = Form(...),
    mask: UploadFile = File(None),
    model: Text = Form(None),
    n: int = Form(None),
    response_format: Text = Form(None),
    size: Text = Form(None),
    user: Text = Form(None),
    timeout: float = Form(None),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesEditsHandler().handle_request(
        request=request,
        images_edit_request=ImagesEditRequest.model_validate(
            {
                "image": await image.read(),
                "prompt": prompt,
                "mask": await mask.read(),
                "model": model,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
                "timeout": timeout,
            }
        ),
        settings=settings,
    )


@router.post("/images/variations")
async def images_variations(
    request: Request,
    image: UploadFile = File(...),
    model: Text = Form(None),
    n: int = Form(None),
    response_format: Text = Form(None),
    size: Text = Form(None),
    user: Text = Form(None),
    timeout: float = Form(None),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesVariationsHandler().handle_request(
        request=request,
        images_variations_request=ImagesVariationsRequest.model_validate(
            {
                "image": await image.read(),
                "model": model,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
                "timeout": timeout,
            }
        ),
        settings=settings,
    )
