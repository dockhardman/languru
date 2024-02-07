import logging
import os
from pathlib import Path
from typing import Text

from pydantic_settings import BaseSettings

from languru.version import VERSION


class Settings(BaseSettings):
    """Settings for the server."""

    # Server
    APP_NAME: Text = "languru-llm"
    SERVICE_NAME: Text = APP_NAME
    APP_VERSION: Text = VERSION
    is_production: bool = False
    is_development: bool = True
    is_testing: bool = False
    debug: bool = is_development
    HOST: Text = "0.0.0.0"
    PORT: int = 8682
    WORKERS: int = 1
    RELOAD: bool = True
    LOG_LEVEL: Text = "debug"
    USE_COLORS: bool = True
    RELOAD_DELAY: float = 5.0
    DATA_DIR: Text = str(Path("./data").absolute())
    ACTION_BASE_URL: Text = "http://localhost:8682"
    AGENT_BASE_URL: Text = "http://localhost:8680"
    # time period to register model
    MODEL_REGISTER_PERIOD: int = 5
    MODEL_REGISTER_FAIL_PERIOD: int = 60

    # Model discovery configuration
    url_model_discovery: Text = f"sqlite:///{DATA_DIR}/languru_model_discovery.db"

    # LLM action configuration
    action: Text = "languru.action.openai.OpenaiAction"

    # Resources configuration
    openai_available: bool = True if os.environ.get("OPENAI_API_KEY") else False


settings = Settings()

logger = logging.getLogger(settings.SERVICE_NAME)
