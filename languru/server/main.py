import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Sequence, Text, cast

import httpx
from fastapi import FastAPI
from openai.types import Model

from languru.config import logger as languru_logger
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
    console,
    init_logger_config,
    init_paths,
    pretty_print_app_routes,
)
from languru.server.utils.common import get_value_from_app


async def register_model_periodically(
    model: Model,
    period: int,
    agent_base_url: Text,
    logger: Optional[logging.Logger] = None,
    model_register_fail_period: int = 60,
):
    logger = languru_logger if logger is None else logger
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
            await asyncio.sleep(float(model_register_fail_period))


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    settings = get_value_from_app(app, key="settings", value_typing=ServerBaseSettings)
    logger = get_value_from_app(
        app, key="logger", value_typing=logging.Logger, default=languru_logger
    )
    # Initialize server
    # Initialize paths
    init_paths(settings)
    # Initialize logger
    init_logger_config(settings)

    if isinstance(settings, LlmSettings):
        from languru.action.base import ModelDeploy
        from languru.action.utils import load_action

        # Load action class
        app.state.action = app.extra["action"] = action = load_action(
            settings.action, logger=logger, device=settings.device, dtype=settings.dtype
        )
        # Register models periodically
        if settings.AGENT_BASE_URL:
            action.model_deploys = cast(Sequence[ModelDeploy], action.model_deploys)
            for model_deploy in action.model_deploys:
                asyncio.create_task(
                    register_model_periodically(
                        model=Model(
                            id=model_deploy.model_deploy_name,
                            created=int(time.time()),
                            object="model",
                            owned_by=settings.LLM_BASE_URL,
                        ),
                        period=settings.MODEL_REGISTER_PERIOD,
                        agent_base_url=settings.AGENT_BASE_URL,
                    )
                )
    if isinstance(settings, AgentSettings):
        from languru.resources.model.discovery import ModelDiscovery

        # Touch database
        model_discovery = ModelDiscovery.from_url(settings.url_model_discovery)
        model_discovery.touch()
        app.state.model_discovery = model_discovery

    yield


def create_app(settings: "ServerBaseSettings", **kwargs):
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
        lifespan=app_lifespan,
    )
    app.state.settings = app.extra["settings"] = settings
    app.state.logger = app.extra["logger"] = logging.getLogger(settings.APP_NAME)
    app.state.app_type = app.extra["app_type"] = settings.APP_TYPE

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    from languru.server.api.v1 import router as api_v1_router

    app.include_router(router=api_v1_router, prefix="/v1")

    return app


def run_app(settings: "ServerBaseSettings", **kwargs):
    import uvicorn

    app_str = "languru.server.main:app"

    if settings.is_development or settings.is_testing:
        languru_logger.info("Running server in development mode")
        uvicorn.run(
            app_str,
            host=settings.HOST,
            port=settings.PORT or settings.DEFAULT_PORT,
            workers=settings.WORKERS,
            reload=settings.RELOAD,
            log_level=settings.LOG_LEVEL,
            use_colors=settings.USE_COLORS,
            reload_delay=settings.RELOAD_DELAY,
        )
    else:
        languru_logger.info("Running server in production mode")
        uvicorn.run(
            app_str,
            host=settings.HOST,
            port=settings.PORT or settings.DEFAULT_PORT,
            workers=settings.WORKERS,
        )


__server_base_settings__ = ServerBaseSettings(DEFAULT_PORT=8000)
app: "FastAPI"
if __server_base_settings__.APP_TYPE == AppType.llm:
    app = create_app(LlmSettings())
    pretty_print_app_routes(app)
elif __server_base_settings__.APP_TYPE == AppType.agent:
    app = create_app(AgentSettings())
    pretty_print_app_routes(app)
else:
    console.print(
        "The APP_TYPE environment variable is not set. "
        + "You might want to set it in values of "
        + f"{', '.join([m for m in AppType.__members__])} "
        + "to define the type of FastAPI app to run."
    )
