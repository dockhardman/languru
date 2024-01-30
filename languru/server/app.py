from fastapi import FastAPI

from languru.server.config import logger, settings


def create_app():
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
    )
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
