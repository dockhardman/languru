import asyncio
import importlib
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Text, Type

import httpx
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai.types import (
    Completion,
    CreateEmbeddingResponse,
    Model,
    ModerationCreateResponse,
)
from pyassorted.asyncio.executor import run_func, run_generator

from languru.action.base import ActionBase
from languru.exceptions import ModelNotFound
from languru.llm.config import init_logger_config, logger, settings
from languru.types.chat.completions import ChatCompletionRequest
from languru.types.completions import CompletionRequest
from languru.types.embeddings import EmbeddingRequest
from languru.types.moderations import ModerationRequest


async def register_model_periodically(model: Model, period: int, agent_base_url: Text):
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_base_url}/v1/models/register",
                    json=model.model_dump(),
                )
                response.raise_for_status()
                await asyncio.sleep(float(period))
        except httpx.HTTPError as e:
            logger.error(f"Failed to register model '{model.id}': {e}")
            await asyncio.sleep(float(settings.MODEL_REGISTER_FAIL_PERIOD))


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Initialize server
    # Check if logs directory exists, if not create it
    if Path(settings.logs_dir).is_dir() is False:
        Path(settings.logs_dir).mkdir(parents=True, exist_ok=True, mode=0o770)
    # Check if data directory exists, if not create it
    if Path(settings.DATA_DIR).is_dir() is False:
        Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True, mode=0o770)
    # Initialize logger
    init_logger_config()

    # Load action class
    logger.info(f"Loading action class '{settings.action}'")
    action_module_path, action_class_name = settings.action.rsplit(".", 1)
    action_cls: Type["ActionBase"] = getattr(
        importlib.import_module(action_module_path), action_class_name
    )
    if issubclass(action_cls, ActionBase) is False:
        raise ValueError(
            f"Action class '{settings.action}' is not a subclass of ActionBase"
        )
    action = action_cls()
    if action.model_deploys is None:
        raise ValueError("Action model_deploys is not defined")
    app.state.action = action

    # Register models periodically
    for model_deploy in action.model_deploys:
        asyncio.create_task(
            register_model_periodically(
                model=Model(
                    id=model_deploy.model_deploy_name,
                    created=int(time.time()),
                    object="model",
                    owned_by=settings.ENDPOINT_URL or settings.ACTION_BASE_URL,
                ),
                period=settings.MODEL_REGISTER_PERIOD,
                agent_base_url=settings.AGENT_BASE_URL,
            )
        )

    yield


def create_app():
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
        lifespan=app_lifespan,
    )

    @app.post("/chat/completions")
    async def chat_completions(
        request: Request,
        chat_completion_request: ChatCompletionRequest = Body(...),
    ):  # -> openai.types.chat.ChatCompletion | openai.types.chat.ChatCompletionChunk
        if getattr(request.app.state, "action", None) is None:
            raise ValueError("Action is not initialized")
        action: "ActionBase" = request.app.state.action
        try:
            chat_completion_request.model = action.get_model_name(
                chat_completion_request.model
            )
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Stream
        if chat_completion_request.stream is True:
            return StreamingResponse(
                run_generator(
                    action.chat_stream_sse,
                    **chat_completion_request.model_dump(exclude_none=True),
                ),
                media_type="application/stream+json",
            )

        # Normal
        else:
            chat_completion = await run_func(
                action.chat, **chat_completion_request.model_dump(exclude_none=True)
            )
            return chat_completion

    @app.post("/completions")
    async def completions(
        request: Request, completion_request: CompletionRequest = Body(...)
    ) -> Completion:
        if getattr(request.app.state, "action", None) is None:
            raise ValueError("Action is not initialized")
        action: "ActionBase" = request.app.state.action
        try:
            completion_request.model = action.get_model_name(completion_request.model)
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        completion = await run_func(
            action.text_completion, **completion_request.model_dump(exclude_none=True)
        )
        return completion

    @app.post("/embeddings")
    async def embeddings(
        request: Request, embedding_request: EmbeddingRequest = Body(...)
    ) -> CreateEmbeddingResponse:
        if getattr(request.app.state, "action", None) is None:
            raise ValueError("Action is not initialized")
        action: "ActionBase" = request.app.state.action
        try:
            embedding_request.model = action.get_model_name(embedding_request.model)
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        embedding = await run_func(
            action.embeddings, **embedding_request.model_dump(exclude_none=True)
        )
        return embedding

    @app.post("/moderations")
    async def request_moderations(
        request: Request, moderation_request: ModerationRequest = Body(...)
    ) -> ModerationCreateResponse:
        if getattr(request.app.state, "action", None) is None:
            raise ValueError("Action is not initialized")
        action: "ActionBase" = request.app.state.action
        try:
            moderation_request.model = action.get_model_name(moderation_request.model)
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        moderation = await run_func(
            action.moderations, **moderation_request.model_dump(exclude_none=True)
        )
        return moderation

    return app


app = create_app()


def run_app():
    import uvicorn

    app_str = "languru.llm.app:app"
    # Determine port
    port = settings.PORT or settings.DEFAULT_PORT

    if settings.is_development or settings.is_testing:
        logger.info("Running server in development mode")
        uvicorn.run(
            app_str,
            host=settings.HOST,
            port=port,
            workers=settings.WORKERS,
            reload=settings.RELOAD,
            log_level=settings.LOG_LEVEL,
            use_colors=settings.USE_COLORS,
            reload_delay=settings.RELOAD_DELAY,
        )
    else:
        logger.info("Running server in production mode")
        uvicorn.run(
            app,
            host=settings.HOST,
            port=port,
            workers=settings.WORKERS,
        )


if __name__ == "__main__":
    run_app()
