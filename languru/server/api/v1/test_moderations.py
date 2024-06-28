from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


@pytest.fixture
def mocked_openai_moderation_create():
    from openai.resources.moderations import Moderations

    from languru.examples.return_values._openai import return_moderation_create

    with patch.object(
        Moderations, "create", MagicMock(return_value=return_moderation_create)
    ):
        yield


def test_app_moderation(test_client, mocked_openai_moderation_create):
    moderation_call = {"input": "I want to kill them."}
    response = test_client.post("/v1/moderations", json=moderation_call)
    assert response.status_code == 200
