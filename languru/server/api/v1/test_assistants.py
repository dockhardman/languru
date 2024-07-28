import pytest
from fastapi.testclient import TestClient
from openai.types.beta.assistant import Assistant

from tests.conftest import *  # noqa: F401, F403


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


def test_assistants_apis(test_client):
    # Create an assistant
    res = test_client.post(
        "/v1/assistants",
        json={
            "model": "gpt-4o-mini",
            "description": (
                "You are a personal math tutor. "
                + "Respond briefly and concisely to the user's questions."
            ),
            "name": "Math Tutor",
        },
    )
    res.raise_for_status()
    assistant = Assistant.model_validate(res.json())

    # Retrieve the assistant
    res = test_client.get("/v1/assistants")
    res.raise_for_status()
    assistant_list = [Assistant.model_validate(item) for item in res.json()["data"]]
    assert len(assistant_list) == 1
    assert assistant_list[0].id == assistant.id
    res = test_client.get(f"/v1/assistants/{assistant.id}")
    res.raise_for_status()
    assert Assistant.model_validate(res.json()).id == assistant.id

    # Update the assistant
    res = test_client.post(
        f"/v1/assistants/{assistant.id}", json={"description": "Updated description."}
    )
    res.raise_for_status()
    assistant_updated = Assistant.model_validate(res.json())
    assert assistant_updated.description == "Updated description."

    # Delete the assistant
    res = test_client.delete(f"/v1/assistants/{assistant.id}")
    res.raise_for_status()
    assert res.json()["id"] == assistant.id

    # Retrieve the assistant again
    res = test_client.get(f"/v1/assistants/{assistant.id}")
    assert res.status_code == 404
