from concurrent.futures import ThreadPoolExecutor

from fastapi import Request


def depends_executor(request: "Request") -> "ThreadPoolExecutor":
    from languru.server.config import APP_STATE_EXECUTOR
    from languru.server.utils.common import get_value_from_app

    return get_value_from_app(
        request.app, key=APP_STATE_EXECUTOR, value_typing=ThreadPoolExecutor
    )
