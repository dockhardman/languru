from typing import Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from pyassorted.asyncio.executor import run_func

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.embeddings import EmbeddingRequest
from languru.types.organizations import OrganizationType

router = APIRouter()


def depends_openai_client_embedding_request(
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    embedding_request: EmbeddingRequest = Body(
        ...,
        openapi_examples={
            "Quick embedding": {
                "summary": "Quick embedding",
                "description": "Embedding request",
                "value": {
                    "model": "text-embedding-ada-002",
                    "input": "The food was delicious and the waiter...",
                },
            }
        },
    ),
) -> Tuple[OpenAI, EmbeddingRequest]:
    if org_type is None:
        org_type = openai_clients.org_from_model(embedding_request.model)

    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")
    else:
        openai_client = openai_clients.org_to_openai_client(org_type)
        return (openai_client, embedding_request)


class EmbeddingHandler:
    async def handle_request(
        self,
        request: "Request",
        *args,
        embedding_request: "EmbeddingRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> "CreateEmbeddingResponse":
        return await run_func(
            openai_client.embeddings.create,
            **embedding_request.model_dump(exclude_none=True),
        )


@router.post("/embeddings")
async def text_completions(
    request: Request,
    openai_client_embedding_request: Tuple[OpenAI, EmbeddingRequest] = Depends(
        depends_openai_client_embedding_request
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> CreateEmbeddingResponse:
    return await EmbeddingHandler().handle_request(
        request=request,
        embedding_request=openai_client_embedding_request[1],
        openai_client=openai_client_embedding_request[0],
        settings=settings,
    )
