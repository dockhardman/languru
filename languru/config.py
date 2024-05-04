import logging

from pydantic_settings import BaseSettings
from rich.console import Console


class Settings(BaseSettings):
    logger_name: str = "languru"
    debug: bool = True


settings = Settings()

logger = logging.getLogger(settings.logger_name)
console = Console()
