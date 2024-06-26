import io
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from openai.resources.images import Images
from openai.types import ImagesResponse
from PIL import Image

from languru.types.images import (
    ImagesEditRequest,
    ImagesGenerationsRequest,
    ImagesVariationsRequest,
)


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


@pytest.fixture(scope="module")
def test_client():
    import languru.server.app

    with TestClient(languru.server.app.app) as client:
        yield client


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


def test_app_images_generations(test_client, mocked_openai_images_generate_create):
    request_call = ImagesGenerationsRequest.model_validate(
        {
            "model": "dall-e-2",
            "prompt": "A cute baby sea otter",
            "size": "256x256",
        }
    )
    response = test_client.post(
        "/v1/images/generations", json=request_call.model_dump(exclude_none=True)
    )
    assert response.status_code == 200


def test_app_images_edits(test_client, mocked_openai_images_edit_create):
    request_call = ImagesEditRequest.model_validate(
        {
            "image": dummy_png(),
            "prompt": "A cute baby sea otter wearing a beret",
            "mask": make_png(),
            "model": "dall-e-2",
        }
    )
    response = test_client.post("/v1/images/edits", files=request_call.to_files_form())
    assert response.status_code == 200


def test_app_images_variations(test_client, mocked_openai_images_variation_create):
    request_call = ImagesVariationsRequest.model_validate(
        {
            "image": ("otter.png", dummy_png(), "image/png"),
            "model": "dall-e-2",
        }
    )
    response = test_client.post(
        "/v1/images/variations", files=request_call.to_files_form()
    )
    assert response.status_code == 200
