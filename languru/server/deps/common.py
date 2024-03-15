from typing import TYPE_CHECKING

from fastapi import Request

if TYPE_CHECKING:
    from languru.server.config import ServerBaseSettings


def app_settings(request: "Request") -> "ServerBaseSettings":
    from languru.server.utils.common import get_value_from_app
    from languru.server.config import ServerBaseSettings

    return get_value_from_app(
        request.app, key="settings", value_typing=ServerBaseSettings
    )
