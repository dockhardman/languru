import time
from logging import Logger
from typing import Any, Dict, List, Optional, Sequence, Text, Tuple, Union

from fastapi import Body, Depends
from fastapi import Path as QueryPath
from fastapi import Query, Request
from fastapi.exceptions import HTTPException
from openai import AzureOpenAI, OpenAI, OpenAIError
from openai.types import Model
from openai.types.beta.threads.run import Run as ThreadsRun
from pyassorted.asyncio.executor import run_func
from pydantic import BaseModel

from languru.config import logger as languru_logger
from languru.examples.openapi.chat import chat_openapi_examples
from languru.exceptions import (
    CredentialsNotProvided,
    ModelNotFound,
    NotFound,
    OrganizationNotFound,
)
from languru.openai_plugins.clients.anthropic import AnthropicOpenAI
from languru.openai_plugins.clients.google import GoogleOpenAI
from languru.openai_plugins.clients.groq import GroqOpenAI
from languru.openai_plugins.clients.pplx import PerplexityOpenAI
from languru.openai_plugins.clients.voyage import VoyageOpenAI
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import APP_STATE_SETTINGS
from languru.server.deps.openai_backend import depends_openai_backend
from languru.server.utils.common import get_value_from_app, to_openapi_examples
from languru.types.chat.completions import ChatCompletionRequest
from languru.types.models import (
    MODELS_ANTHROPIC,
    MODELS_AZURE_OPENAI,
    MODELS_GOOGLE,
    MODELS_GROQ,
    MODELS_OPENAI,
    MODELS_PERPLEXITY,
    MODELS_VOYAGE,
)
from languru.types.openai_threads import ThreadsRunCreate
from languru.types.organizations import OrganizationType, to_org_type
from languru.utils.common import display_object


class OpenaiModels:
    _models: List[Model]

    def models(self, model: Optional[Text] = None) -> List["Model"]:
        """Returns the supported models based on the organization type."""

        if model is not None:
            for m in self._models:
                if m.id == model:
                    return [m.model_copy()]
            else:
                err_body = {
                    "error": {
                        "message": f"The model '{model}' does not exist",
                        "type": "invalid_request_error",
                        "param": "model",
                        "code": "model_not_found",
                    }
                }
                raise ModelNotFound(
                    f"Error code: 404 - {err_body}",
                )

        else:
            return [m.model_copy() for m in self._models]

    def model_add(
        self, models: Union[Dict, "Model", Sequence[Dict], Sequence["Model"]]
    ) -> None:
        """Adds a new model to the supported models."""

        if isinstance(models, Dict):
            self._models.append(Model.model_validate(models))
            return
        elif isinstance(models, BaseModel):
            self._models.append(Model.model_validate(models.model_dump()))
            return

        for m in models:
            if isinstance(m, BaseModel):
                self._models.append(Model.model_validate(m.model_dump()))
            else:
                self._models.append(Model.model_validate(m))

    def model_remove(self, models: Union[Text, List[Text]]) -> None:
        """Removes a model from the supported models."""

        if isinstance(models, Text):
            models = [models]
        self._models[:] = [m for m in self._models if m.id not in models]

    def model_strip_org(
        self, model: Text, org: Optional[Union[Text, OrganizationType]] = None
    ) -> Text:
        """Strips the organization type from the model name."""

        orgs: List[OrganizationType] = [
            to_org_type(o) if isinstance(o, Text) else o
            for o in ([org] if org is not None else list(OrganizationType))
        ]
        model = model.strip()
        model_lower = model.lower()
        for _org in orgs:
            if model_lower.startswith(f"{_org.value.lower()}/"):
                return model.split("/", 1)[-1]
        return model


class OpenaiDepends:
    def depends_org_type(
        self,
        request: Request,
        api_type: Optional[Text] = Query(None),
        org: Optional[Text] = Query(None),
        org_type: Optional[Text] = Query(None),
        organization: Optional[Text] = Query(None),
        organization_type: Optional[Text] = Query(None),
    ) -> Optional[OrganizationType]:
        """Returns the OpenAI client based on the request parameters."""

        logger = get_value_from_app(
            request.app,
            key=APP_STATE_SETTINGS,
            value_typing=Logger,
            default=languru_logger,
        )
        organization_type = (
            organization_type or organization or org_type or org or api_type
        )

        out: Optional[OrganizationType] = None
        if organization_type is not None:
            out = to_org_type(organization_type)
            logger.debug(f"Organization type: '{out}'.")
        return out


class OpenaiClients(OpenaiModels, OpenaiDepends):
    def __init__(self, *args, **kwargs):
        self._oai_client: Optional["OpenAI"] = None
        self._aoai_client: Optional["AzureOpenAI"] = None
        self._ant_client: Optional["AnthropicOpenAI"] = None
        self._gg_client: Optional["GoogleOpenAI"] = None
        self._gq_client: Optional["GroqOpenAI"] = None
        self._pplx_client: Optional["PerplexityOpenAI"] = None
        self._vg_client: Optional["VoyageOpenAI"] = None
        self._models: List["Model"] = []

        self.init_openai_clients()

    def init_openai_clients(self) -> None:
        self.init_openai_client()
        self.init_azure_openai_client()
        self.init_anthropic_openai_client()
        self.init_google_openai_client()
        self.init_groq_openai_client()
        self.init_perplexity_openai_client()
        self.init_voyage_openai_client()

    def init_openai_client(self) -> None:
        try:
            self._oai_client = OpenAI()
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.OPENAI.value,
                    }
                )
                for m in MODELS_OPENAI
            ]
            self.model_add(_models)
        except OpenAIError:
            languru_logger.warning("OpenAI client not initialized.")

    def init_azure_openai_client(self) -> None:
        try:
            self._aoai_client = AzureOpenAI(api_version="2024-02-01")
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.AZURE.value,
                    }
                )
                for m in MODELS_AZURE_OPENAI
            ]
            self.model_add(_models)
        except OpenAIError:
            languru_logger.warning("Azure OpenAI client not initialized.")

    def init_anthropic_openai_client(self) -> None:
        try:
            self._ant_client = AnthropicOpenAI()
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.ANTHROPIC.value,
                    }
                )
                for m in MODELS_ANTHROPIC
            ]
            self.model_add(_models)
        except CredentialsNotProvided:
            languru_logger.warning("Anthropic OpenAI client not initialized.")

    def init_google_openai_client(self) -> None:
        try:
            self._gg_client = GoogleOpenAI()
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.GOOGLE.value,
                    }
                )
                for m in MODELS_GOOGLE
            ]
            self.model_add(_models)
        except CredentialsNotProvided:
            languru_logger.warning("Google OpenAI client not initialized.")

    def init_groq_openai_client(self) -> None:
        try:
            self._gq_client = GroqOpenAI()
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.GROQ.value,
                    }
                )
                for m in MODELS_GROQ
            ]
            self.model_add(_models)
        except CredentialsNotProvided:
            languru_logger.warning("Groq OpenAI client not initialized.")

    def init_perplexity_openai_client(self) -> None:
        try:
            self._pplx_client = PerplexityOpenAI()
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.PERPLEXITY.value,
                    }
                )
                for m in MODELS_PERPLEXITY
            ]
            self.model_add(_models)
        except CredentialsNotProvided:
            languru_logger.warning("Perplexity OpenAI client not initialized.")

    def init_voyage_openai_client(self) -> None:
        try:
            self._vg_client = VoyageOpenAI()
            _models = [
                Model.model_validate(
                    {
                        "id": m,
                        "created": int(time.time()),
                        "object": "model",
                        "owned_by": OrganizationType.VOYAGE.value,
                    }
                )
                for m in MODELS_VOYAGE
            ]
            self.model_add(_models)
        except CredentialsNotProvided:
            languru_logger.warning("Voyage OpenAI client not initialized.")

    def org_in_model_name(self, model: Text) -> Optional[OrganizationType]:
        _model = (model.strip() if model else None) or None
        organization_type: Optional[OrganizationType] = None

        # Try to extract organization type from the model name
        if _model and "/" in _model:
            might_org = _model.split("/")[0]
            try:
                organization_type = to_org_type(might_org)
                languru_logger.debug(
                    f"Organization type: '{organization_type}' of '{_model}'."
                )
            except OrganizationNotFound:
                pass
        return organization_type

    def org_in_supported_models(self, model: Text) -> Optional[OrganizationType]:
        _model = (model.strip() if model else None) or None
        if _model is None:
            return None
        # Try search supported models
        organization_type: Optional[OrganizationType] = None
        for _c, _org in (
            (self._oai_client, OrganizationType.OPENAI),
            (self._aoai_client, OrganizationType.AZURE),
            (self._ant_client, OrganizationType.ANTHROPIC),
            (self._gg_client, OrganizationType.GOOGLE),
            (self._gq_client, OrganizationType.GROQ),
            (self._pplx_client, OrganizationType.PERPLEXITY),
            (self._vg_client, OrganizationType.VOYAGE),
        ):
            if _c is None:
                continue
            if isinstance(_c, OpenAI):
                if model in MODELS_OPENAI:
                    organization_type = _org
                    languru_logger.debug(
                        f"Organization type: '{organization_type}' of '{_model}'."
                    )
                    break
            elif isinstance(_c, AzureOpenAI):
                if model in MODELS_AZURE_OPENAI:
                    organization_type = _org
                    languru_logger.debug(
                        f"Organization type: '{organization_type}' of '{_model}'."
                    )
                    break
            elif hasattr(_c, "models") and hasattr(_c.models, "supported_models"):
                if model in _c.models.supported_models:  # type: ignore
                    organization_type = _org
                    languru_logger.debug(
                        f"Organization type: '{organization_type}' of '{_model}'."
                    )
                    break
        return organization_type

    def org_from_model(self, model: Text) -> Optional[OrganizationType]:
        """Returns the organization type based on the model name."""

        organization_type: Optional[OrganizationType] = None
        if organization_type is None:
            organization_type = self.org_in_model_name(model)
        if organization_type is None:
            organization_type = self.org_in_supported_models(model)
        return organization_type

    def org_to_openai_client(
        self, org: Union[Text, "OrganizationType", Any]
    ) -> "OpenAI":
        """Returns the OpenAI client based on the organization type."""

        if not isinstance(org, OrganizationType):
            org = to_org_type(org)
        _client: Optional["OpenAI"] = None
        if org == OrganizationType.OPENAI:
            _client = self._oai_client
        elif org == OrganizationType.AZURE:
            _client = self._aoai_client
        elif org == OrganizationType.ANTHROPIC:
            _client = self._ant_client
        elif org == OrganizationType.GOOGLE:
            _client = self._gg_client
        elif org == OrganizationType.GROQ:
            _client = self._gq_client
        elif org == OrganizationType.PERPLEXITY:
            _client = self._pplx_client
        elif org == OrganizationType.VOYAGE:
            _client = self._vg_client
        else:
            raise OrganizationNotFound(f"Unknown organization: '{org}'.")
        if _client is None:
            raise OrganizationNotFound(
                f"Organization '{org}' client not not initialized."
            )
        return _client

    def default_openai_client(self) -> "OpenAI":
        """Returns the default OpenAI client."""

        # logger.warning("No organization type specified. Using OpenAI by default.")
        if self._oai_client is None:
            raise OrganizationNotFound("OpenAI client not initialized.")
        return self._oai_client


openai_clients = OpenaiClients()


def openai_client_from_model(
    model: Text,
    *,
    org_type: Optional[OrganizationType] = None,
    openai_clients: OpenaiClients = openai_clients,
) -> Tuple[OpenAI, OrganizationType, Text]:
    """Returns the OpenAI client and the model name without organization type."""

    if org_type is None:
        org_type = openai_clients.org_from_model(model)
    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")

    model_without_org = openai_clients.model_strip_org(model, org_type)
    openai_client = openai_clients.org_to_openai_client(org_type)
    return (openai_client, org_type, model_without_org)


def depends_openai_client_chat_completion_request(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    chat_completion_request: ChatCompletionRequest = Body(
        ...,
        openapi_examples=to_openapi_examples(chat_openapi_examples),
    ),
) -> Tuple[OpenAI, ChatCompletionRequest]:
    """Returns the OpenAI client and the chat completion request."""

    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    openai_client, org_type, chat_completion_request.model = openai_client_from_model(
        chat_completion_request.model, org_type=org_type
    )

    logger.debug(
        "Depends OpenAI client chat completion request: "
        + f"organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{chat_completion_request.model}'"
    )
    return (openai_client, chat_completion_request)


async def depends_thread_id_run_openai_client_backend(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to create a run in.",
    ),
    run_create_request: ThreadsRunCreate = Body(
        ...,
        description="The parameters for creating a run.",
    ),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Tuple[Text, ThreadsRun, OpenAI, OpenaiBackend]:
    """Returns the thread ID, the OpenAI threads run, the OpenAI client, and the backend."""  # noqa: E501

    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    # Retrieve the model if not specified
    if run_create_request.model is None:
        logger.debug(
            "No model specified. Using assistant "
            + f"'{run_create_request.assistant_id}' model."
        )
        try:
            assistant_retrieved = await run_func(
                openai_backend.assistants.retrieve,
                assistant_id=run_create_request.assistant_id,
            )
            run_create_request.model = assistant_retrieved.model
        except NotFound:
            raise HTTPException(status_code=404, detail="Assistant not found.")

    # Retrieve the OpenAI client and the model name without organization type
    openai_client, org_type, run_create_request.model = openai_client_from_model(
        run_create_request.model, org_type=org_type
    )

    # Create the OpenAI threads run
    run = run_create_request.to_openai_run(thread_id=thread_id, status="queued")

    logger.debug(
        "Depends OpenAI client threads run create request: "
        + f"organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{run_create_request.model}'"
    )
    return (thread_id, run, openai_client, openai_backend)
