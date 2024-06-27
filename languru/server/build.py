import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from languru.config import logger as languru_logger
from languru.config import settings as languru_settings
from languru.server.config import (
    ServerBaseSettings,
    init_logger_config,
    init_paths,
    pretty_print_app_routes,
)
from languru.server.deps.openai_clients import OpenaiClients
from languru.server.utils.common import get_value_from_app


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    settings = get_value_from_app(app, key="settings", value_typing=ServerBaseSettings)
    init_paths(settings)
    init_logger_config(settings)
    yield


def create_app(settings: "ServerBaseSettings", **kwargs):
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
        lifespan=app_lifespan,
    )
    app.state.languru_settings = app.extra["languru_settings"] = languru_settings
    app.state.settings = app.extra["settings"] = settings
    app.state.logger = app.extra["logger"] = logging.getLogger(settings.APP_NAME)
    app.state.openai_clients = app.extra["openai_clients"] = OpenaiClients()

    @app.get("/")
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    from languru.server.api.v1 import router as api_v1_router

    app.include_router(router=api_v1_router, prefix="/v1")

    pretty_print_app_routes(app)
    return app


def run_app(settings: "ServerBaseSettings", **kwargs):
    import uvicorn

    app_str = "languru.server.app:app"

    if settings.is_development or settings.is_testing:
        languru_logger.info("Running server in development mode")
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
        languru_logger.info("Running server in production mode")
        uvicorn.run(
            app_str,
            host=settings.HOST,
            port=settings.PORT,
            workers=settings.WORKERS,
        )
