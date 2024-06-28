from typing import Annotated, Optional, Text

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Path as PathParam
from fastapi import Query, Request
from openai.pagination import SyncPage

from languru.exceptions import ModelNotFound
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.model import Model
from languru.types.organizations import OrganizationType

router = APIRouter()


class ModelsHandler:
    async def handle_models_request(
        self,
        request: "Request",
        id: Optional[Text],
        owned_by: Optional[Text],
        created_from: Optional[int],
        created_to: Optional[int],
        organization_type: Optional["OrganizationType"],
        settings: "ServerBaseSettings",
    ) -> "SyncPage[Model]":
        return SyncPage.model_validate(
            {
                "data": [m.model_dump() for m in openai_clients.models()],
                "object": "list",
            }
        )


class RetrieveModelHandler:
    async def handle_model_request(
        self,
        request: "Request",
        *args,
        model: Text,
        organization_type: Optional["OrganizationType"],
        settings: "ServerBaseSettings",
    ) -> Model:
        try:
            models_list = openai_clients.models(model=model)
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        if len(models_list) == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        return Model.model_validate(models_list[0].model_dump())


@router.get("/models", summary="List models")
async def get_models(
    request: Request,
    id: Annotated[Text | None, "Model ID"] = Query(None),
    owned_by: Annotated[Text | None, "Model owned by"] = Query(None),
    created_from: Annotated[int | None, "Model created from timestamp"] = Query(None),
    created_to: Annotated[int | None, "Model created to timestamp"] = Query(None),
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    settings: ServerBaseSettings = Depends(app_settings),
) -> SyncPage[Model]:
    return await ModelsHandler().handle_models_request(
        request=request,
        id=id,
        owned_by=owned_by,
        created_from=created_from,
        created_to=created_to,
        organization_type=org_type,
        settings=settings,
    )


@router.get("/models/{model}", summary="Retrieve model")
async def get_model(
    request: Request,
    model: Text = PathParam(...),
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Model:
    return await RetrieveModelHandler().handle_model_request(
        request=request, model=model, organization_type=org_type, settings=settings
    )
