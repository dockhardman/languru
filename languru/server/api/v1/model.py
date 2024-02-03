import time
from typing import Text

from fastapi import APIRouter
from fastapi import Path as PathParam
from fastapi import Request
from openai.pagination import SyncPage
from openai.types import Model, ModelDeleted

router = APIRouter()


@router.get("/models", summary="List models")
async def get_models(request: Request) -> SyncPage[Model]:
    return {
        "object": "list",
        "data": [
            {
                "id": "model-id-0",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization-owner",
            },
            {
                "id": "model-id-1",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization-owner",
            },
            {
                "id": "model-id-2",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai",
            },
        ],
        "object": "list",
    }


@router.get("/models/{model}", summary="Retrieve model")
async def get_model(request: Request, model: Text = PathParam(...)) -> Model:
    return {
        "id": "gpt-3.5-turbo-instruct",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "openai",
    }


@router.delete("/models/{model}", summary="Delete a fine-tuned model")
async def delete_model(request: Request, model: Text = PathParam(...)) -> ModelDeleted:
    return {
        "id": "ft:gpt-3.5-turbo:acemeco:suffix:abc123",
        "object": "model",
        "deleted": True,
    }
