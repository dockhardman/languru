import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI

from languru.config import logger as languru_logger
from languru.config import settings as languru_settings
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import (
    APP_STATE_EXECUTOR,
    APP_STATE_LANGURU_SETTINGS,
    APP_STATE_LOGGER,
    APP_STATE_OPENAI_BACKEND,
    APP_STATE_OPENAI_CLIENTS,
    APP_STATE_SETTINGS,
    ServerBaseSettings,
    init_logger_config,
    init_paths,
    pretty_print_app_routes,
)
from languru.server.deps.openai_clients import OpenaiClients
from languru.server.utils.common import get_value_from_app


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # App initialization
    settings = get_value_from_app(
        app, key=APP_STATE_SETTINGS, value_typing=ServerBaseSettings
    )
    init_paths(settings)
    init_logger_config(settings)

    # OpenAI clients initialization
    openai_backend = get_value_from_app(
        app, key=APP_STATE_OPENAI_BACKEND, value_typing=OpenaiBackend
    )
    openai_backend.touch()

    # Yield
    with refresh_executor_of_app(app):  # Refresh thread pool executor
        yield


def create_app(settings: "ServerBaseSettings", **kwargs):
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
        lifespan=app_lifespan,
    )
    __logger = logging.getLogger(settings.APP_NAME)
    __openai_clients = OpenaiClients()
    __openai_backend = OpenaiBackend(url=settings.OPENAI_BACKEND_URL)
    __executor = ThreadPoolExecutor(
        max_workers=1,
        thread_name_prefix="languru.server.app.state.executor",
    )
    app.extra[APP_STATE_LANGURU_SETTINGS] = languru_settings
    app.extra[APP_STATE_SETTINGS] = settings
    app.extra[APP_STATE_LOGGER] = __logger
    app.extra[APP_STATE_OPENAI_CLIENTS] = __openai_clients
    app.state.openai_backend = app.extra[APP_STATE_OPENAI_BACKEND] = __openai_backend
    app.extra[APP_STATE_EXECUTOR] = __executor
    setattr(app.state, APP_STATE_LANGURU_SETTINGS, languru_settings)
    setattr(app.state, APP_STATE_SETTINGS, settings)
    setattr(app.state, APP_STATE_LOGGER, __logger)
    setattr(app.state, APP_STATE_OPENAI_CLIENTS, __openai_clients)
    setattr(app.state, APP_STATE_OPENAI_BACKEND, __openai_backend)
    setattr(app.state, APP_STATE_EXECUTOR, __executor)

    @app.get("/")
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/stats")
    async def stats():
        return {
            "status": "ok",
            "pending_tasks": __executor._work_queue.qsize(),
            "total_workers": len(__executor._threads),
            "idle_workers": __executor._idle_semaphore._value,
        }

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


def refresh_executor_of_app(app: "FastAPI") -> "ThreadPoolExecutor":
    """Refresh the executor of the app."""

    executor = get_value_from_app(
        app, key=APP_STATE_EXECUTOR, value_typing=ThreadPoolExecutor
    )
    if executor._shutdown:
        executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="languru.server.app.state.executor",
        )
        app.extra[APP_STATE_EXECUTOR] = executor
        setattr(app.state, APP_STATE_EXECUTOR, executor)
    return executor
