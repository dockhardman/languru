from fastapi import APIRouter, Body, Depends, Request
from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from pyassorted.asyncio.executor import run_func

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.embeddings import EmbeddingRequest

router = APIRouter()


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
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> CreateEmbeddingResponse:
    return await EmbeddingHandler().handle_request(
        request=request,
        embedding_request=embedding_request,
        openai_client=openai_client,
        settings=settings,
    )
