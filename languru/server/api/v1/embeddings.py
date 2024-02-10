import math
import random
import time

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from openai.types import CreateEmbeddingResponse
from pyassorted.asyncio.executor import run_func
from yarl import URL

from languru.resources.model.discovery import ModelDiscovery
from languru.server.config import settings
from languru.types.embeddings import EmbeddingRequest

router = APIRouter()


@router.post("/embeddings")
async def text_completions(
    request: Request,
    embedding_request: EmbeddingRequest = Body(
        ...,
        example={
            "input": "The food was delicious and the waiter...",
            "model": "text-embedding-ada-002",
            "encoding_format": "float",
        },
    ),
) -> CreateEmbeddingResponse:
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    models = await run_func(
        model_discovery.list,
        id=embedding_request.model,
        created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
    )
    if len(models) == 0:
        raise HTTPException(
            status_code=404, detail=f"Model '{embedding_request.model}' not found"
        )

    model = random.choice(models)
    url = URL(model.owned_by).with_path("/embeddings")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            str(url), json=embedding_request.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        return CreateEmbeddingResponse(**response.json())
