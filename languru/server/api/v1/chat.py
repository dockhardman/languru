from logging import Logger
from typing import Optional, Tuple

from fastapi import APIRouter, Body, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pyassorted.asyncio.executor import run_func, run_generator

from languru.config import logger as languru_logger
from languru.examples.openapi.chat import chat_openapi_examples
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.server.utils.common import get_value_from_app, to_openapi_examples
from languru.types.chat.completions import ChatCompletionRequest
from languru.types.organizations import OrganizationType
from languru.utils.common import display_object
from languru.utils.http import simple_sse_encode

router = APIRouter()


def depends_openai_client_chat_completion_request(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    chat_completion_request: ChatCompletionRequest = Body(
        ...,
        openapi_examples=to_openapi_examples(chat_openapi_examples),
    ),
) -> Tuple[OpenAI, ChatCompletionRequest]:
    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    if org_type is None:
        org_type = openai_clients.org_from_model(chat_completion_request.model)
    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")

    chat_completion_request.model = openai_clients.model_strip_org(
        chat_completion_request.model, org_type
    )
    openai_client = openai_clients.org_to_openai_client(org_type)
    logger.debug(
        f"Organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{chat_completion_request.model}'"
    )
    return (openai_client, chat_completion_request)


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
                simple_sse_encode,
                await run_func(openai_client.chat.completions.create, **params),
            ),
            media_type="application/stream+json",
        )


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    openai_client_chat_completion_request: Tuple[
        OpenAI, ChatCompletionRequest
    ] = Depends(depends_openai_client_chat_completion_request),
    settings: ServerBaseSettings = Depends(app_settings),
):  # -> openai.types.chat.ChatCompletion | openai.types.chat.ChatCompletionChunk
    return await ChatCompletionHandler().handle_request(
        request=request,
        chat_completion_request=openai_client_chat_completion_request[1],
        settings=settings,
        openai_client=openai_client_chat_completion_request[0],
    )
