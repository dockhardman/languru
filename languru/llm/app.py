import importlib
from contextlib import asynccontextmanager
from typing import Type

from fastapi import FastAPI

from languru.action.base import ActionBase
from languru.llm.config import logger, settings


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
    app.state.action = action

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
