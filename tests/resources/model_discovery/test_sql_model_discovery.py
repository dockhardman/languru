from typing import Text

import pytest

from languru.resources.model_discovery.base import ModelDiscovery
from languru.resources.model_discovery.sql import SqlModelDiscovery


@pytest.mark.parametrize(
    "url",
    [
        "sqlite:///:memory:",
        "sqlite:///tmp/test.db",
        "sqlite:///test.db",
        # "postgresql://user:pass@localhost:5432/dbname",  # Not supported yet
        # "postgres://user:pass@localhost:5432/dbname",  # Not supported yet
        # "mysql://user:pass@localhost:3306/dbname",  # Not supported yet
    ],
)
def test_sql_model_discovery_builder(url: Text):
    assert isinstance(ModelDiscovery.from_url(url), SqlModelDiscovery)


def test_sqlite_model_discovery_init(session_id_fixture: Text):
    # Create path in `/tmp` directory
    url = f"sqlite:////tmp/{session_id_fixture}.db"
    model_discovery = ModelDiscovery.from_url(url)
    assert isinstance(model_discovery, SqlModelDiscovery)
    model_discovery.touch()
