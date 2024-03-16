import logging
import math
import time
from typing import Annotated, Any, Dict, List, Optional, Text, cast

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Path as PathParam
from fastapi import Query, Request
from openai.pagination import SyncPage
from openai.types import ModelDeleted
from pyassorted.asyncio.executor import run_func

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.deps.common import app_settings
from languru.server.utils.common import get_value_from_app
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
        settings: "ServerBaseSettings",
    ) -> "SyncPage[Model]":
        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_models_agent(
                request=request,
                id=id,
                owned_by=owned_by,
                created_from=created_from,
                created_to=created_to,
                settings=settings,
            )
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_models_llm(
                request=request,
                id=id,
                owned_by=owned_by,
                created_from=created_from,
                created_to=created_to,
                settings=settings,
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_models_agent(
        self,
        request: "Request",
        id: Optional[Text],
        owned_by: Optional[Text],
        created_from: Optional[int],
        created_to: Optional[int],
        settings: "AgentSettings",
    ) -> "SyncPage[Model]":
        from languru.resources.model.discovery import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )

        if created_from is None and created_to is not None:
            created_from = math.floor(
                time.time() - float(settings.MODEL_REGISTER_PERIOD)
            )
        retrieved_models = await run_func(
            model_discovery.list,
            id=id,
            owned_by=owned_by,
            created_from=created_from,
            created_to=created_to,
        )
        return SyncPage(data=retrieved_models, object="list")

    async def handle_models_llm(
        self,
        request: "Request",
        id: Optional[Text],
        owned_by: Optional[Text],
        created_from: Optional[int],
        created_to: Optional[int],
        settings: "LlmSettings",
    ) -> "SyncPage[Model]":
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )
        models: List["Model"] = []
        if action.model_deploys:
            for model_deploy in action.model_deploys:
                models.append(
                    Model(
                        id=model_deploy.model_deploy_name,
                        created=int(time.time()),
                        object="model",
                        owned_by=settings.LLM_BASE_URL,
                    )
                )
        return SyncPage(data=models, object="list")


class RetrieveModelHandler:
    async def handle_model_request(
        self,
        request: "Request",
        model: Text,
        settings: "ServerBaseSettings",
    ) -> Model:
        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_model_agent(
                request=request, model=model, settings=settings
            )
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_model_llm(
                request=request, model=model, settings=settings
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_model_agent(
        self,
        request: "Request",
        model: Text,
        settings: "AgentSettings",
    ) -> Model:
        from languru.resources.model.discovery import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        retrieved_model = await run_func(model_discovery.retrieve, id=model)
        if retrieved_model is None:
            raise HTTPException(status_code=404, detail="Model not found")
        return retrieved_model

    async def handle_model_llm(
        self,
        request: "Request",
        model: Text,
        settings: "LlmSettings",
    ) -> Model:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )
        logger = get_value_from_app(
            request.app,
            key="logger",
            value_typing=logging.Logger,
            default=logging.getLogger(settings.APP_NAME),
        )
        try:
            model = action.get_model_name(model)
        except ModelNotFound as e:
            logger.debug(f"Model not found: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        return Model(
            id=model,
            created=int(time.time()),
            object="model",
            owned_by=settings.LLM_BASE_URL,
        )


class ModelRegisterHandler:
    async def handle_model_register_request(
        self, request: "Request", model: Model, settings: "ServerBaseSettings"
    ) -> Dict[Text, Any]:
        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_model_register_agent(
                request=request, model=model, settings=settings
            )
        if settings.APP_TYPE == AppType.llm:
            raise HTTPException(
                status_code=403,
                detail="Model registration not allowed for this app server type",
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_model_register_agent(
        self, request: "Request", model: Model, settings: "AgentSettings"
    ) -> Dict[Text, Any]:
        from languru.resources.model.discovery import ModelDiscovery

        model_discovery: "ModelDiscovery" = get_value_from_app(
            request.app, key="model_discovery", value_typing=ModelDiscovery
        )
        logger = get_value_from_app(
            request.app, key="logger", value_typing=logging.Logger
        )
        try:
            await run_func(model_discovery.register, model)
            return {"acknowledge": True}
        except Exception as e:
            logger.exception(e)
            logger.error(f"Failed to register model: {e}")
            raise HTTPException(status_code=500, detail="Failed to register model")


@router.get("/models", summary="List models")
async def get_models(
    request: Request,
    id: Annotated[Text | None, "Model ID"] = Query(None),
    owned_by: Annotated[Text | None, "Model owned by"] = Query(None),
    created_from: Annotated[int | None, "Model created from timestamp"] = Query(None),
    created_to: Annotated[int | None, "Model created to timestamp"] = Query(None),
    settings: ServerBaseSettings = Depends(app_settings),
) -> SyncPage[Model]:
    return await ModelsHandler().handle_models_request(
        request=request,
        id=id,
        owned_by=owned_by,
        created_from=created_from,
        created_to=created_to,
        settings=settings,
    )


@router.get("/models/{model}", summary="Retrieve model")
async def get_model(
    request: Request,
    model: Text = PathParam(...),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Model:
    return await RetrieveModelHandler().handle_model_request(
        request=request, model=model, settings=settings
    )


@router.delete("/models/{model}", summary="Delete a fine-tuned model")
async def delete_model(request: Request, model: Text = PathParam(...)) -> ModelDeleted:
    # Not implemented
    return ModelDeleted(id=model, deleted=True, object="model")


@router.post("/models/register", summary="Register models")
async def register_models(
    request: Request,
    model: Model,
    settings: ServerBaseSettings = Depends(app_settings),
):
    return await ModelRegisterHandler().handle_model_register_request(
        request=request, model=model, settings=settings
    )
