from fastapi import Request

from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import APP_STATE_OPENAI_BACKEND
from languru.server.utils.common import get_value_from_app


def depends_openai_backend(request: Request) -> "OpenaiBackend":
    openai_backend = get_value_from_app(
        request.app, key=APP_STATE_OPENAI_BACKEND, value_typing=OpenaiBackend
    )
    return openai_backend
