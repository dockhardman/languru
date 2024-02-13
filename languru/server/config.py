import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Text

import pytz
from colorama import Fore, Style, init
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
    logging_level: Text = "DEBUG"
    logs_dir: Text = "logs"
    HOST: Text = "0.0.0.0"
    DEFAULT_PORT: int = 8680
    PORT: Optional[int] = None
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


class IsoDatetimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        record_datetime = datetime.fromtimestamp(record.created).astimezone(
            pytz.timezone("Asia/Taipei")
        )
        t = record_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        z = record_datetime.strftime("%z")
        ms_exp = record_datetime.microsecond // 1000
        s = f"{t}.{ms_exp:03d}{z}"
        return s


class ColoredIsoDatetimeFormatter(IsoDatetimeFormatter):
    COLORS = {
        "WARNING": Fore.YELLOW,
        "INFO": Fore.GREEN,
        "DEBUG": Fore.BLUE,
        "CRITICAL": Fore.RED,
        "ERROR": Fore.RED,
    }
    MSG_COLORS = {
        "WARNING": Fore.YELLOW,
        "INFO": Fore.GREEN,
        "CRITICAL": Fore.RED,
        "ERROR": Fore.RED,
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                self.COLORS[levelname] + f"{levelname:8s}" + Style.RESET_ALL
            )
            record.name = Fore.BLUE + record.name + Style.RESET_ALL
            if not isinstance(record.msg, Text):
                record.msg = str(record.msg)
            if levelname in self.MSG_COLORS:
                record.msg = self.COLORS[levelname] + record.msg + Style.RESET_ALL
        return super(ColoredIsoDatetimeFormatter, self).format(record)


def default_logging_config():
    d = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colered_formatter": {
                "()": ColoredIsoDatetimeFormatter,
                "format": "%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
            },
            "message_formatter": {"format": "%(message)s"},
            "file_formatter": {
                "()": IsoDatetimeFormatter,
                "format": "%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
            },
        },
        "handlers": {
            "console_handler": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "colered_formatter",
            },
            "file_handler": {
                "level": settings.logging_level,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": Path(settings.logs_dir)
                .joinpath(f"{settings.APP_NAME}.log")
                .resolve(),
                "formatter": "file_formatter",
                "maxBytes": 2097152,
                "backupCount": 20,
            },
            "error_handler": {
                "level": "WARNING",
                "class": "logging.FileHandler",
                "filename": Path(settings.logs_dir)
                .joinpath(f"{settings.APP_NAME}.error.log")
                .resolve(),
                "formatter": "file_formatter",
            },
        },
        "loggers": {
            "languru": {
                "level": "DEBUG",
                "handlers": ["file_handler", "error_handler", "console_handler"],
                "propagate": True,
            },
            settings.APP_NAME: {
                "level": "DEBUG",
                "handlers": ["file_handler", "error_handler", "console_handler"],
                "propagate": True,
            },
        },
    }
    return d


def init_logger_config():
    if settings.USE_COLORS:
        init(autoreset=True)
    logging.config.dictConfig(default_logging_config())
    return logger
