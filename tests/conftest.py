import os
import uuid
from datetime import datetime
from typing import Text

import pytest
import pytz
from dotenv import load_dotenv

load_dotenv()

test_session_id = (
    datetime.now(tz=pytz.UTC).strftime("%y%m%d%H%M%S")
    + str(uuid.uuid4()).split("-")[0].upper()
)
test_env_vars = {
    "logger_name": "languru_test",
    "is_test": True,
    "is_dev": False,
    "is_prod": False,
    "is_staging": False,
    "is_ci": True,
    "pytest": True,
    "pytest_session": True,
}


def set_test_env_vars():
    for k, v in test_env_vars.items():
        os.environ[k] = str(v)
        os.environ[k.upper()] = str(v)


def set_openai_backend_settings():
    os.environ["OPENAI_BACKEND_URL"] = f"sqlite:////tmp/openai-{test_session_id}.db"


@pytest.fixture(scope="session")
def session_id_fixture() -> Text:
    """Generate a unique session ID for test sessions."""

    return test_session_id


set_test_env_vars()
set_openai_backend_settings()

__all__ = ["test_session_id"]
