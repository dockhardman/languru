from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from languru.resources.model.discovery import ModelDiscovery
from languru.server.config import logger, settings


@asynccontextmanager
async def maybe_openai_available(app: FastAPI):
    # Initialize server
    data_dir = Path(settings.DATA_DIR)
    if data_dir.is_dir() is False:
        data_dir.mkdir(parents=True, exist_ok=True, mode=0o770)

    # Touch database
    model_discover = ModelDiscovery.from_url(settings.url_model_discovery)
    model_discover.touch()
    app.state.model_discover = model_discover

    yield


def create_app():
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
        lifespan=maybe_openai_available,
    )

    from languru.server.api.v1 import router as api_v1_router

    app.include_router(router=api_v1_router, prefix="/api/v1")
    return app


app = create_app()


def run_app():
    import uvicorn

    app_str = "languru.server.app:app"

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
