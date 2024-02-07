import logging
import os
from pathlib import Path
from typing import Text

from pydantic_settings import BaseSettings

from languru.version import VERSION


class Settings(BaseSettings):
    """Settings for the server."""

    # Server
    APP_NAME: Text = "languru-server"
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
    DATA_DIR: Text = str(Path("./data").absolute())

    # Model discovery configuration
    url_model_discovery: Text = f"sqlite:///{DATA_DIR}/languru_model_discovery.db"
    MODEL_REGISTER_PERIOD: int = 10

    # Resources configuration
    openai_available: bool = True if os.environ.get("OPENAI_API_KEY") else False


settings = Settings()

logger = logging.getLogger(settings.SERVICE_NAME)
