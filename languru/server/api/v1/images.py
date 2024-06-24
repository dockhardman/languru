from typing import Text

from fastapi import APIRouter, Body, Depends, File, Form, Request, UploadFile
from openai import OpenAI
from openai.types import ImagesResponse
from pyassorted.asyncio.executor import run_func

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
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
        *args,
        images_generations_request: "ImagesGenerationsRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ImagesResponse:
        return await run_func(
            openai_client.images.generate,
            **images_generations_request.model_dump(exclude_none=True),
        )


class ImagesEditsHandler:
    async def handle_request(
        self,
        request: "Request",
        *args,
        images_edit_request: "ImagesEditRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ImagesResponse:
        return await run_func(
            openai_client.images.edit,
            **images_edit_request.model_dump(exclude_none=True),
        )


class ImagesVariationsHandler:
    async def handle_request(
        self,
        request: "Request",
        *args,
        images_variations_request: "ImagesVariationsRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> ImagesResponse:
        return await run_func(
            openai_client.images.create_variation,
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
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesGenerationsHandler().handle_request(
        request=request,
        images_generations_request=images_generations_request,
        openai_client=openai_client,
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
    openai_client=Depends(openai_clients.depends_openai_client),
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
        openai_client=openai_client,
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
    openai_client=Depends(openai_clients.depends_openai_client),
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
        openai_client=openai_client,
        settings=settings,
    )
