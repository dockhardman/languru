from typing import Text

from pydantic_settings import BaseSettings

from general_llm_stack.version import VERSION


class Settings(BaseSettings):
    """Settings for the server."""

    # Server
    APP_NAME: Text = "general_llm_stack_server"
    SERVICE_NAME: Text = APP_NAME
    APP_VERSION: Text = VERSION
    is_production: bool = False
    is_development: bool = True
    is_testing: bool = False
    debug: bool = is_development
    HOST: Text = "0.0.0.0"
    PORT: int = 8680
    WORKERS: int = 1
    RELOAD: bool = True
    LOG_LEVEL: Text = "debug"
    USE_COLORS: bool = True
    RELOAD_DELAY: float = 5.0


settings = Settings()
