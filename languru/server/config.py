import logging
import logging.config
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Text

import pytz
from colorama import Fore, Style, init
from pydantic_settings import BaseSettings
from rich.console import Console
from rich.table import Table

from languru.version import VERSION

if TYPE_CHECKING:
    from fastapi import FastAPI

console = Console()


# string enum
class AppType(str, Enum):
    llm = "llm"
    agent = "agent"


class ServerBaseSettings(BaseSettings):
    """Settings for the server."""

    # Server
    APP_NAME: Text = "languru"
    SERVICE_NAME: Text = APP_NAME
    APP_VERSION: Text = VERSION
    APP_TYPE: Optional[Literal[AppType.llm, AppType.agent]] = None
    is_production: bool = False
    is_development: bool = True
    is_testing: bool = False
    debug: bool = is_development
    logging_level: Text = "DEBUG"
    logs_dir: Text = "logs"
    HOST: Text = "0.0.0.0"
    DEFAULT_PORT: int
    PORT: Optional[int] = None
    WORKERS: int = 1
    RELOAD: bool = True
    LOG_LEVEL: Text = "debug"
    USE_COLORS: bool = True
    RELOAD_DELAY: float = 5.0
    DATA_DIR: Text = str(Path("./data").absolute())

    # Resources configuration
    openai_available: bool = True if os.environ.get("OPENAI_API_KEY") else False


class LlmSettings(ServerBaseSettings):
    APP_NAME: Text = "languru-llm"
    SERVICE_NAME: Text = APP_NAME
    APP_TYPE: Literal[AppType.llm] = AppType.llm
    DEFAULT_PORT: int = 8682

    # LLM Server Configuration
    LLM_BASE_URL: Text = "http://0.0.0.0:8682/v1"
    ACTION_BASE_URL: Text = LLM_BASE_URL  # Deprecated, use LLM_BASE_URL instead
    ACTION_ENDPOINT_URL: Text = LLM_BASE_URL  # Deprecated, use LLM_BASE_URL instead
    AGENT_BASE_URL: Optional[Text] = None
    MODEL_REGISTER_PERIOD: int = 10
    MODEL_REGISTER_FAIL_PERIOD: int = 60

    # Hardware device configuration
    device: Optional[Text] = None
    dtype: Optional[Text] = None

    # LLM action configuration
    action: Text = "languru.action.openai.OpenaiAction"


class AgentSettings(ServerBaseSettings):
    # Server
    APP_NAME: Text = "languru-agent"
    SERVICE_NAME: Text = APP_NAME
    APP_TYPE: Literal[AppType.agent] = AppType.agent
    DEFAULT_PORT: int = 8680
    DATA_DIR: Text = str(Path("./data").absolute())

    # Model discovery configuration
    MODEL_REGISTER_PERIOD: int = 10
    url_model_discovery: Text = f"sqlite:///{DATA_DIR}/languru_model_discovery.db"


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


def default_logging_config(settings: "ServerBaseSettings"):
    d = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored_formatter": {
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
                "formatter": "colored_formatter",
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


def init_logger_config(settings: "ServerBaseSettings") -> None:
    if settings.USE_COLORS:
        init(autoreset=True)
    logging.config.dictConfig(default_logging_config(settings))
    return


def init_paths(settings: "ServerBaseSettings") -> None:
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True, mode=0o770)
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True, mode=0o770)
    return


def pretty_print_app_routes(app: "FastAPI") -> None:
    """Show all routes in the FastAPI app."""

    table = Table(title="\nLanguru Routes")
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta", no_wrap=True)

    path_names = [
        (str(getattr(route, "path", "null")), str(getattr(route, "name", "null")))
        for route in app.routes
    ]
    url_list = [
        {"path": path_name[0], "name": path_name[1]} for path_name in path_names
    ]
    url_list.sort(key=lambda item: item["path"])
    for _url_item in url_list:
        table.add_row(_url_item["path"], _url_item["name"])
    console.print(table)
