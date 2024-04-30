import importlib
import io
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from openai.resources.images import Images
from openai.types import ImagesResponse
from PIL import Image

import languru.server.main
from languru.server.config import AppType
from languru.types.images import (
    ImagesEditRequest,
    ImagesGenerationsRequest,
    ImagesVariationsRequest,
)

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def dummy_png() -> bytes:
    image = Image.new("RGB", (256, 256), color=(255, 255, 255))
    byte_stream = io.BytesIO()
    image.save(byte_stream, format="PNG")
    return byte_stream.getvalue()


def make_png() -> bytes:
    mask_image = Image.new(
        "RGBA", (256, 256), color=(255, 255, 255, 0)
    )  # RGBA format, fully transparent
    mask_byte_stream = io.BytesIO()
    mask_image.save(mask_byte_stream, format="PNG")
    return mask_byte_stream.getvalue()


@pytest.fixture
def llm_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.llm)


@pytest.fixture
def agent_env(monkeypatch: "MonkeyPatch"):
    monkeypatch.setenv("APP_TYPE", AppType.agent)


@pytest.fixture
def mocked_openai_images_generate_create():
    with patch.object(
        Images,
        "generate",
        MagicMock(
            return_value=ImagesResponse.model_validate(
                {"created": int(time.time()), "data": [{"url": "https://..."}]}
            )
        ),
    ):
        yield


@pytest.fixture
def mocked_openai_images_edit_create():
    with patch.object(
        Images,
        "edit",
        MagicMock(
            return_value=ImagesResponse.model_validate(
                {"created": int(time.time()), "data": [{"url": "https://..."}]}
            )
        ),
    ):
        yield


@pytest.fixture
def mocked_openai_images_variation_create():
    with patch.object(
        Images,
        "create_variation",
        MagicMock(
            return_value=ImagesResponse.model_validate(
                {"created": int(time.time()), "data": [{"url": "https://..."}]}
            )
        ),
    ):
        yield


@pytest.fixture
def mocked_model_discovery_list():
    from languru.resources.model.discovery import ModelDiscovery, SqlModelDiscovery
    from languru.types.model import Model

    return_model_discovery_list = [
        Model(
            id="dall-e-2",
            created=int(time.time()) - 1,
            object="model",
            owned_by="http://0.0.0.0:8682/v1",
        ),
    ]
    with patch.object(
        ModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ), patch.object(
        SqlModelDiscovery, "list", MagicMock(return_value=return_model_discovery_list)
    ):
        yield


def test_llm_app_images_generations(llm_env, mocked_openai_images_generate_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = ImagesGenerationsRequest.model_validate(
            {
                "model": "dall-e-2",
                "prompt": "A cute baby sea otter",
                "size": "256x256",
            }
        )
        response = client.post(
            "/v1/images/generations", json=request_call.model_dump(exclude_none=True)
        )
        assert response.status_code == 200


def test_llm_app_images_edits(llm_env, mocked_openai_images_edit_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = ImagesEditRequest.model_validate(
            {
                "image": dummy_png(),
                "prompt": "A cute baby sea otter wearing a beret",
                "mask": make_png(),
                "model": "dall-e-2",
            }
        )
        response = client.post("/v1/images/edits", files=request_call.to_files_form())
        assert response.status_code == 200


def test_llm_app_images_variations(llm_env, mocked_openai_images_variation_create):
    importlib.reload(languru.server.main)

    with TestClient(languru.server.main.app) as client:
        request_call = ImagesVariationsRequest.model_validate(
            {
                "image": ("otter.png", dummy_png(), "image/png"),
                "model": "dall-e-2",
            }
        )
        response = client.post(
            "/v1/images/variations", files=request_call.to_files_form()
        )
        assert response.status_code == 200
