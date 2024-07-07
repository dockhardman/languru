import time
from logging import Logger
from typing import Any, Dict, List, Optional, Sequence, Text, Union

from fastapi import Query, Request
from openai import AzureOpenAI, OpenAI, OpenAIError
from openai.types import Model
from pydantic import BaseModel

from languru.config import logger as languru_logger
from languru.exceptions import (
    CredentialsNotProvided,
    ModelNotFound,
    OrganizationNotFound,
)
from languru.openai_plugins.clients.anthropic import AnthropicOpenAI
from languru.openai_plugins.clients.google import GoogleOpenAI
from languru.openai_plugins.clients.groq import GroqOpenAI
from languru.openai_plugins.clients.pplx import PerplexityOpenAI
from languru.openai_plugins.clients.voyage import VoyageOpenAI
from languru.server.utils.common import get_value_from_app
from languru.types.models import (
    MODELS_ANTHROPIC,
    MODELS_AZURE_OPENAI,
    MODELS_GOOGLE,
    MODELS_GROQ,
    MODELS_OPENAI,
    MODELS_PERPLEXITY,
    MODELS_VOYAGE,
)
from languru.types.organizations import OrganizationType, to_org_type


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
            request.app, key="logger", value_typing=Logger, default=languru_logger
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


# class Model(BaseModel):
#     id: str
#     """The model identifier, which can be referenced in the API endpoints."""

#     created: int
#     """The Unix timestamp (in seconds) when the model was created."""

#     object: Literal["model"]
#     """The object type, which is always "model"."""

#     owned_by: str
#     """The organization that owns the model."""
