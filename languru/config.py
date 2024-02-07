import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    logger_name: str = "languru"


settings = Settings()

logger = logging.getLogger(settings.logger_name)
