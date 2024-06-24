from fastapi import APIRouter, Body, Depends, Request
from openai import OpenAI
from openai.types import ModerationCreateResponse
from pyassorted.asyncio.executor import run_func

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.moderations import ModerationRequest

router = APIRouter()


class ModerationsHandler:
    async def handle_moderations_request(
        self,
        request: "Request",
        *args,
        moderation_request: "ModerationRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
    ) -> "ModerationCreateResponse":
        return await run_func(
            openai_client.moderations.create,
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
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ModerationCreateResponse:
    return await ModerationsHandler().handle_moderations_request(
        request=request,
        moderation_request=moderation_request,
        openai_client=openai_client,
        settings=settings,
    )
