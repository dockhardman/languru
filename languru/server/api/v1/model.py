import time
from typing import TYPE_CHECKING, Text

from fastapi import APIRouter
from fastapi import Path as PathParam
from fastapi import Request
from openai.pagination import SyncPage
from openai.types import ModelDeleted

from languru.config import logger
from languru.types.model import Model

if TYPE_CHECKING:
    from languru.resources.model.discovery import ModelDiscovery

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
    # Not implemented
    return ModelDeleted(id=model, deleted=True, object="model")


@router.post("/models/register", summary="Register models")
async def register_models(request: Request, model: Model):
    print(model)
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    registered_model = model_discovery.register(model)
    logger.debug(f"Registered model: {registered_model}")
    return {"acknowledge": True}
