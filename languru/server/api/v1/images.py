from logging import Logger
from typing import Optional, Text, Tuple

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
from openai import OpenAI
from openai.types import ImagesResponse
from pyassorted.asyncio.executor import run_func

from languru.config import logger as languru_logger
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.server.utils.common import get_value_from_app
from languru.types.images import (
    ImagesEditRequest,
    ImagesGenerationsRequest,
    ImagesVariationsRequest,
)
from languru.types.organizations import OrganizationType
from languru.utils.common import display_object

router = APIRouter()


def depends_openai_client_model(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    model: Text = Form(None),
) -> Tuple[OpenAI, Text]:
    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    if org_type is None:
        org_type = openai_clients.org_from_model(model)
    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")

    openai_client = openai_clients.org_to_openai_client(org_type)
    model = openai_clients.model_strip_org(model, org_type)
    logger.debug(
        f"Organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{model}'"
    )
    return (openai_client, model)


def depends_openai_client_images_generations_request(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
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
) -> Tuple[OpenAI, ImagesGenerationsRequest]:
    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    if org_type is None:
        org_type = openai_clients.org_from_model(images_generations_request.model)
    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")

    openai_client = openai_clients.org_to_openai_client(org_type)
    images_generations_request.model = openai_clients.model_strip_org(
        images_generations_request.model, org_type
    )
    logger.debug(
        f"Organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{images_generations_request.model}'"
    )
    return (openai_client, images_generations_request)


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
    openai_client_images_generations_request: Tuple[
        OpenAI, ImagesGenerationsRequest
    ] = Depends(depends_openai_client_images_generations_request),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesGenerationsHandler().handle_request(
        request=request,
        images_generations_request=openai_client_images_generations_request[1],
        openai_client=openai_client_images_generations_request[0],
        settings=settings,
    )


@router.post("/images/edits")
async def images_edits(
    request: Request,
    image: UploadFile = File(...),
    prompt: Text = Form(...),
    mask: UploadFile = File(None),
    n: int = Form(None),
    response_format: Text = Form(None),
    size: Text = Form(None),
    user: Text = Form(None),
    timeout: float = Form(None),
    openai_client_model: Tuple[OpenAI, Text] = Depends(depends_openai_client_model),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesEditsHandler().handle_request(
        request=request,
        images_edit_request=ImagesEditRequest.model_validate(
            {
                "image": await image.read(),
                "prompt": prompt,
                "mask": await mask.read(),
                "model": openai_client_model[1],
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
                "timeout": timeout,
            }
        ),
        openai_client=openai_client_model[0],
        settings=settings,
    )


@router.post("/images/variations")
async def images_variations(
    request: Request,
    image: UploadFile = File(...),
    n: int = Form(None),
    response_format: Text = Form(None),
    size: Text = Form(None),
    user: Text = Form(None),
    timeout: float = Form(None),
    openai_client_model: Tuple[OpenAI, Text] = Depends(depends_openai_client_model),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ImagesResponse:
    return await ImagesVariationsHandler().handle_request(
        request=request,
        images_variations_request=ImagesVariationsRequest.model_validate(
            {
                "image": await image.read(),
                "model": openai_client_model[1],
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
                "timeout": timeout,
            }
        ),
        openai_client=openai_client_model[0],
        settings=settings,
    )
