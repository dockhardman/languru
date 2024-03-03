import math
import time
from typing import TYPE_CHECKING, Annotated, Text

from fastapi import APIRouter, HTTPException
from fastapi import Path as PathParam
from fastapi import Query, Request
from openai.pagination import SyncPage
from openai.types import ModelDeleted
from pyassorted.asyncio.executor import run_func

from languru.server.config import logger, settings
from languru.types.model import Model

if TYPE_CHECKING:
    from languru.resources.model.discovery import ModelDiscovery

router = APIRouter()


@router.get("/models", summary="List models")
async def get_models(
    request: Request,
    id: Annotated[Text | None, "Model ID"] = Query(None),
    owned_by: Annotated[Text | None, "Model owned by"] = Query(None),
    created_from: Annotated[int | None, "Model created from timestamp"] = Query(None),
    created_to: Annotated[int | None, "Model created to timestamp"] = Query(None),
) -> SyncPage[Model]:
    if created_from is None and created_to is not None:
        created_from = math.floor(time.time() - float(settings.MODEL_REGISTER_PERIOD))
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    retrieved_models = await run_func(
        model_discovery.list,
        id=id,
        owned_by=owned_by,
        created_from=created_from,
        created_to=created_to,
    )
    return SyncPage(data=retrieved_models, object="list")


@router.get("/models/{model}", summary="Retrieve model")
async def get_model(request: Request, model: Text = PathParam(...)) -> Model:
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    retrieved_model = await run_func(model_discovery.retrieve, id=model)
    if retrieved_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return retrieved_model


@router.delete("/models/{model}", summary="Delete a fine-tuned model")
async def delete_model(request: Request, model: Text = PathParam(...)) -> ModelDeleted:
    # Not implemented
    return ModelDeleted(id=model, deleted=True, object="model")


@router.post("/models/register", summary="Register models")
async def register_models(request: Request, model: Model):
    if getattr(request.app.state, "model_discovery", None) is None:
        raise ValueError("Model discovery is not initialized")
    model_discovery: "ModelDiscovery" = request.app.state.model_discovery
    try:
        await run_func(model_discovery.register, model)
        return {"acknowledge": True}
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to register model: {e}")
        raise HTTPException(status_code=500, detail="Failed to register model")
