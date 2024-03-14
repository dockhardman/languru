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
from languru.server.config_agent import settings
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


# @app.post("/chat/completions")
# async def chat_completions(
#     request: Request,
#     chat_completion_request: ChatCompletionRequest = Body(...),
# ):  # -> openai.types.chat.ChatCompletion | openai.types.chat.ChatCompletionChunk
#     if getattr(request.app.state, "action", None) is None:
#         raise ValueError("Action is not initialized")
#     action: "ActionBase" = request.app.state.action
#     try:
#         chat_completion_request.model = action.get_model_name(
#             chat_completion_request.model
#         )
#     except ModelNotFound as e:
#         raise HTTPException(status_code=404, detail=str(e))

#     # Stream
#     if chat_completion_request.stream is True:
#         return StreamingResponse(
#             run_generator(
#                 action.chat_stream_sse,
#                 **chat_completion_request.model_dump(exclude_none=True),
#             ),
#             media_type="application/stream+json",
#         )

#     # Normal
#     else:
#         chat_completion = await run_func(
#             action.chat, **chat_completion_request.model_dump(exclude_none=True)
#         )
#         return chat_completion
