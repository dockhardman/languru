from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from languru.resources.model.discovery import ModelDiscovery
from languru.server.config import init_logger_config, logger, settings
from languru.utils.socket import check_port, get_available_port


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

    # Touch database
    model_discovery = ModelDiscovery.from_url(settings.url_model_discovery)
    model_discovery.touch()
    app.state.model_discovery = model_discovery

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


app = create_app()


def run_app():
    import uvicorn

    app_str = "languru.server.app:app"
    # Determine port
    if settings.PORT is None:
        port = get_available_port(settings.DEFAULT_PORT)
    else:
        if check_port(settings.PORT) is False:
            raise ValueError(f"The port '{settings.PORT}' is already in use")
        port = settings.PORT

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
        uvicorn.run(app, host=settings.HOST, port=port, workers=settings.WORKERS)


if __name__ == "__main__":
    run_app()
