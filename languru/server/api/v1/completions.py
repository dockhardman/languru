import math
import random
import time

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai.types import Completion
from pyassorted.asyncio.executor import run_func
from yarl import URL

from languru.resources.model.discovery import ModelDiscovery
from languru.server.config import settings
from languru.types.completions import CompletionRequest
from languru.utils.http import requests_stream_lines

router = APIRouter()


@router.post("/completions")
async def text_completions(
    request: Request,
    completions_request: CompletionRequest = Body(
        ...,
        example={
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
        },
    ),
):  # openai.types.Completion
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    models = await run_func(
        model_discovery.list,
        id=completions_request.model,
        created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
    )
    if len(models) == 0:
        raise HTTPException(
            status_code=404, detail=f"Model '{completions_request.model}' not found"
        )

    model = random.choice(models)
    url = URL(model.owned_by).with_path("/completions")
    # Request completion
    # Stream
    if completions_request.stream is True:
        return StreamingResponse(
            requests_stream_lines(
                str(url), data=completions_request.model_dump(exclude_none=True)
            ),
            media_type="application/stream+json",
        )
    # Normal
    else:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                str(url), json=completions_request.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return Completion(**response.json())
