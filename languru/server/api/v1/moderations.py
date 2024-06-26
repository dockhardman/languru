from typing import Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from openai import OpenAI
from openai.types import ModerationCreateResponse
from pyassorted.asyncio.executor import run_func

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.moderations import ModerationRequest
from languru.types.organizations import OrganizationType

router = APIRouter()


def depends_openai_client_moderation_request(
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
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
) -> Tuple[OpenAI, ModerationRequest]:
    if org_type is None:
        org_type = openai_clients.org_from_model(
            moderation_request.model or ModerationRequest.model_fields["model"].default
        )

    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")
    else:
        openai_client = openai_clients.org_to_openai_client(org_type)
        return (openai_client, moderation_request)


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
    openai_client_moderation_request: Tuple[OpenAI, ModerationRequest] = Depends(
        depends_openai_client_moderation_request
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> ModerationCreateResponse:
    return await ModerationsHandler().handle_moderations_request(
        request=request,
        moderation_request=openai_client_moderation_request[1],
        openai_client=openai_client_moderation_request[0],
        settings=settings,
    )
