from logging import Logger
from typing import Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.completion import Completion
from pyassorted.asyncio.executor import run_func, run_generator

from languru.config import logger as languru_logger
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.server.utils.common import get_value_from_app
from languru.types.completions import CompletionRequest
from languru.types.organizations import OrganizationType
from languru.utils.common import display_object
from languru.utils.http import simple_sse_encode

router = APIRouter()


def depends_openai_client_completion_request(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
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
) -> Tuple[OpenAI, CompletionRequest]:
    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    if org_type is None:
        org_type = openai_clients.org_from_model(completion_request.model)
    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")

    openai_client = openai_clients.org_to_openai_client(org_type)
    completion_request.model = openai_clients.model_strip_org(
        completion_request.model, org_type
    )
    logger.debug(
        f"Organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{completion_request.model}'"
    )
    return (openai_client, completion_request)


class TextCompletionHandler:

    async def handle_request(
        self,
        request: "Request",
        *args,
        completion_request: "CompletionRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> Completion | StreamingResponse:
        # Stream
        if completion_request.stream is True:
            return await self.handle_stream(
                request=request,
                completion_request=completion_request,
                openai_client=openai_client,
                settings=settings,
                **kwargs,
            )
        # Normal
        else:
            return await self.handle_normal(
                request=request,
                completion_request=completion_request,
                openai_client=openai_client,
                settings=settings,
                **kwargs,
            )

    async def handle_normal(
        self,
        request: "Request",
        *args,
        completion_request: "CompletionRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> Completion:
        return await run_func(
            openai_client.completions.create,
            completion_request.model_dump(exclude_none=True),
        )

    async def handle_stream(
        self,
        request: "Request",
        *args,
        completion_request: "CompletionRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> StreamingResponse:
        completion_stream_params = completion_request.model_dump(exclude_none=True)
        completion_stream_params.pop("stream", None)
        return StreamingResponse(
            run_generator(
                simple_sse_encode,
                await run_func(
                    openai_client.completions.create,
                    **completion_stream_params,
                    stream=True,
                ),
            ),
            media_type="application/stream+json",
        )


@router.post("/completions")
async def text_completions(
    request: Request,
    openai_client_completion_request: Tuple[OpenAI, CompletionRequest] = Depends(
        depends_openai_client_completion_request
    ),
    settings: ServerBaseSettings = Depends(app_settings),
):  # openai.types.Completion
    return await TextCompletionHandler().handle_request(
        request=request,
        completion_request=openai_client_completion_request[1],
        openai_client=openai_client_completion_request[0],
        settings=settings,
    )
