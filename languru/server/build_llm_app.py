import asyncio
import time
from contextlib import asynccontextmanager
from typing import Sequence, Text, cast

import httpx
from fastapi import FastAPI
from openai.types import Model

from languru.action.base import ModelDeploy
from languru.action.utils import load_action
from languru.server.config import init_logger_config, init_paths
from languru.server.config_llm import logger, settings


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
    # Initialize paths
    init_paths(settings)
    # Initialize logger
    init_logger_config(settings)
    # Load action class
    app.state.action = app.extra["action"] = action = load_action(
        settings.action, logger=logger
    )
    # Register models periodically
    action.model_deploys = cast(Sequence[ModelDeploy], action.model_deploys)
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

    @app.get("/health")
    async def health():
        logger.debug("Health check")
        return {"status": "ok"}

    from languru.server.api.v1 import router as api_v1_router

    app.include_router(router=api_v1_router, prefix="/v1")

    return app


def run_app(app: "FastAPI"):
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
