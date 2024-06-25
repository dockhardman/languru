from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

test_model_name = "text-embedding-ada-002"


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


@pytest.fixture
def mocked_openai_embeddings_create():
    from openai.resources.embeddings import Embeddings as OpenaiEmbeddings

    from languru.examples.return_values._openai import return_embedding

    with patch.object(
        OpenaiEmbeddings,
        "create",
        MagicMock(return_value=return_embedding),
    ):
        yield


def test_app_embedding(test_client):
    embedding_call = {
        "input": ["Hello", "world!"],
        "model": test_model_name,
        "encoding_format": "float",
    }
    response = test_client.post("/v1/embeddings", json=embedding_call)
    assert response.status_code == 200
    assert len(response.json()["data"]) == len(embedding_call["input"])
