import logging
from pathlib import Path
from typing import Text

from languru.server.config import ServerBaseSettings


class Settings(ServerBaseSettings):
    """Settings for the server."""

    # Server
    APP_NAME: Text = "languru-server"
    SERVICE_NAME: Text = APP_NAME
    DEFAULT_PORT: int = 8680
    DATA_DIR: Text = str(Path("./data").absolute())

    # Model discovery configuration
    MODEL_REGISTER_PERIOD: int = 10
    url_model_discovery: Text = f"sqlite:///{DATA_DIR}/languru_model_discovery.db"


settings = Settings()
logger = logging.getLogger(settings.SERVICE_NAME)
