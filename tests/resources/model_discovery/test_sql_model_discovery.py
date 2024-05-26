import time
from typing import Text

import pytest

from languru.resources.model_discovery.base import ModelDiscovery
from languru.resources.model_discovery.sql import SqlModelDiscovery
from languru.types.model import Model


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


def test_sqlite_model_discovery_operation(session_id_fixture: Text):
    url = f"sqlite:////tmp/{session_id_fixture}.db"
    model_discovery = ModelDiscovery.from_url(url)
    assert isinstance(model_discovery, SqlModelDiscovery)
    model_discovery.touch()

    # Register, retrieve and list
    model = model_discovery.register(
        Model.model_validate(
            dict(id="gpt-4o", created=1715367049, object="model", owned_by="system")
        )
    )
    created_at = int(time.time())  # Current time
    assert model_discovery.register(model, created=created_at).created == created_at
    retrieved_model = model_discovery.retrieve(model.id)
    assert retrieved_model is not None
    assert retrieved_model.id == model.id
    assert len(model_discovery.list()) > 0
    assert len(model_discovery.list(id=model.id)) > 0
    assert len(model_discovery.list(id="SHOULD_NOT_EXIST")) == 0
    assert len(model_discovery.list(owned_by=model.owned_by)) > 0
    assert len(model_discovery.list(created_from=created_at)) > 0
    assert len(model_discovery.list(created_from=created_at + 1)) == 0
    assert len(model_discovery.list(created_to=created_at)) > 0
    assert len(model_discovery.list(created_to=created_at - 1)) == 0
