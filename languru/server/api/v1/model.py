from typing import Annotated, Optional, Text

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Path as PathParam
from fastapi import Query, Request
from openai import OpenAI
from openai.pagination import SyncPage

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.model import Model

router = APIRouter()


class ModelsHandler:
    async def handle_models_request(
        self,
        request: "Request",
        id: Optional[Text],
        owned_by: Optional[Text],
        created_from: Optional[int],
        created_to: Optional[int],
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
    ) -> "SyncPage[Model]":
        raise HTTPException(status_code=501, detail="Not implemented")
        # return SyncPage(data=models, object="list")


class RetrieveModelHandler:
    async def handle_model_request(
        self,
        request: "Request",
        *args,
        model: Text,
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
    ) -> Model:
        raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/models", summary="List models")
async def get_models(
    request: Request,
    id: Annotated[Text | None, "Model ID"] = Query(None),
    owned_by: Annotated[Text | None, "Model owned by"] = Query(None),
    created_from: Annotated[int | None, "Model created from timestamp"] = Query(None),
    created_to: Annotated[int | None, "Model created to timestamp"] = Query(None),
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> SyncPage[Model]:
    return await ModelsHandler().handle_models_request(
        request=request,
        id=id,
        owned_by=owned_by,
        created_from=created_from,
        created_to=created_to,
        openai_client=openai_client,
        settings=settings,
    )


@router.get("/models/{model}", summary="Retrieve model")
async def get_model(
    request: Request,
    model: Text = PathParam(...),
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Model:
    return await RetrieveModelHandler().handle_model_request(
        request=request, model=model, openai_client=openai_client, settings=settings
    )
