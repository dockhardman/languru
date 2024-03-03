import math
import random
import time

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai.types.chat.chat_completion import ChatCompletion
from pyassorted.asyncio.executor import run_func
from yarl import URL

from languru.resources.model.discovery import ModelDiscovery
from languru.server.config import settings
from languru.types.chat.completions import ChatCompletionRequest
from languru.utils.http import requests_stream_lines

router = APIRouter()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    chat_completions_request: ChatCompletionRequest = Body(
        ...,
        example={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        },
    ),
):  # -> openai.types.chat.ChatCompletion | openai.types.chat.ChatCompletionChunk
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")

    # Get model name and model destination
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    models = await run_func(
        model_discovery.list,
        id=chat_completions_request.model,
        created_from=math.floor(time.time() - settings.MODEL_REGISTER_PERIOD),
    )
    if len(models) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{chat_completions_request.model}' not found",
        )
    model = random.choice(models)
    url = URL(model.owned_by).with_path("/chat/completions")

    # Request completion
    # Stream
    if chat_completions_request.stream is True:
        return StreamingResponse(
            requests_stream_lines(
                str(url), data=chat_completions_request.model_dump(exclude_none=True)
            ),
            media_type="application/stream+json",
        )
    # Normal
    else:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                str(url), json=chat_completions_request.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return ChatCompletion(**response.json())
