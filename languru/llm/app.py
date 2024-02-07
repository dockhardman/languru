import asyncio
import importlib
import time
from contextlib import asynccontextmanager
from typing import Text, Type

import httpx
from fastapi import FastAPI
from openai.types import Model

from languru.action.base import ActionBase
from languru.llm.config import logger, settings


async def register_model_periodically(model: Model, period: int, agent_base_url: Text):
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_base_url}/api/v1/models/register",
                    json=model.model_dump(),
                )
                response.raise_for_status()
                await asyncio.sleep(float(period))
        except httpx.HTTPError as e:
            logger.error(f"Failed to register model '{model.id}': {e}")
            await asyncio.sleep(float(settings.MODEL_REGISTER_FAIL_PERIOD))


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Load action class
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
                    owned_by=settings.ACTION_BASE_URL,
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

    return app


app = create_app()


def run_app():
    import uvicorn

    app_str = "languru.llm.app:app"

    if settings.is_development or settings.is_testing:
        logger.info("Running server in development mode")
        uvicorn.run(
            app_str,
            host=settings.HOST,
            port=settings.PORT,
            workers=settings.WORKERS,
            reload=settings.RELOAD,
            log_level=settings.LOG_LEVEL,
            use_colors=settings.USE_COLORS,
            reload_delay=settings.RELOAD_DELAY,
        )
    else:
        logger.info("Running server in production mode")
        uvicorn.run(
            app, host=settings.HOST, port=settings.PORT, workers=settings.WORKERS
        )


if __name__ == "__main__":
    run_app()
