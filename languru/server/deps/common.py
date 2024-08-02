from typing import TYPE_CHECKING

from fastapi import Request

from languru.server.config import APP_STATE_SETTINGS

if TYPE_CHECKING:
    from languru.server.config import ServerBaseSettings


def app_settings(request: "Request") -> "ServerBaseSettings":
    from languru.server.config import ServerBaseSettings
    from languru.server.utils.common import get_value_from_app

    return get_value_from_app(
        request.app, key=APP_STATE_SETTINGS, value_typing=ServerBaseSettings
    )
