from fastapi import FastAPI

from general_llm_stack.server.config import settings


def create_app():
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.debug,
        version=settings.APP_VERSION,
    )
    return app


app = create_app()
