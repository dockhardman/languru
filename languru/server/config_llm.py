import logging
from typing import Optional, Text

from languru.server.config import ServerBaseSettings


class Settings(ServerBaseSettings):
    """Settings for the server."""

    # Server
    APP_NAME: Text = "languru-llm"
    SERVICE_NAME: Text = APP_NAME
    DEFAULT_PORT: int = 8682

    # LLM Server Configuration
    ACTION_BASE_URL: Text = "http://localhost:8682"
    ENDPOINT_URL: Text = ""
    AGENT_BASE_URL: Text = "http://localhost:8680"
    MODEL_REGISTER_PERIOD: int = 10
    MODEL_REGISTER_FAIL_PERIOD: int = 60

    # Hardware device configuration
    device: Optional[Text] = None
    dtype: Optional[Text] = None

    # LLM action configuration
    action: Text = "languru.action.openai.OpenaiAction"


settings = Settings()
logger = logging.getLogger(settings.SERVICE_NAME)
