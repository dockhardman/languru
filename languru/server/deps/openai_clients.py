from logging import Logger
from typing import Any, Optional, Text, Union

from fastapi import Body, Query, Request
from openai import AzureOpenAI, OpenAI, OpenAIError

from languru.config import logger as languru_logger
from languru.exceptions import OrganizationNotFound
from languru.openai_plugins.clients.anthropic import AnthropicOpenAI
from languru.openai_plugins.clients.google import GoogleOpenAI
from languru.openai_plugins.clients.groq import GroqOpenAI
from languru.openai_plugins.clients.pplx import PerplexityOpenAI
from languru.openai_plugins.clients.voyage import VoyageOpenAI
from languru.server.utils.common import get_value_from_app
from languru.types.organizations import OrganizationType, to_org_type


class OpenaiClients:
    def __init__(self, *args, **kwargs):
        self._oai_client: Optional["OpenAI"] = None
        self._aoai_client: Optional["AzureOpenAI"] = None
        self._ant_client: Optional["AnthropicOpenAI"] = None
        self._gg_client: Optional["GoogleOpenAI"] = None
        self._gq_client: Optional["GroqOpenAI"] = None
        self._pplx_client: Optional["PerplexityOpenAI"] = None
        self._vg_client: Optional["VoyageOpenAI"] = None

        try:
            self._oai_client = OpenAI()
        except OpenAIError:
            languru_logger.warning("OpenAI client not initialized.")
        try:
            self._aoai_client = AzureOpenAI()
        except OpenAIError:
            languru_logger.warning("Azure OpenAI client not initialized.")
        try:
            self._ant_client = AnthropicOpenAI()
        except OrganizationNotFound:
            languru_logger.warning("Anthropic OpenAI client not initialized.")
        try:
            self._gg_client = GoogleOpenAI()
        except OrganizationNotFound:
            languru_logger.warning("Google OpenAI client not initialized.")
        try:
            self._gq_client = GroqOpenAI()
        except OrganizationNotFound:
            languru_logger.warning("Groq OpenAI client not initialized.")
        try:
            self._pplx_client = PerplexityOpenAI()
        except OrganizationNotFound:
            languru_logger.warning("Perplexity OpenAI client not initialized.")
        try:
            self._vg_client = VoyageOpenAI()
        except OrganizationNotFound:
            languru_logger.warning("Voyage OpenAI client not initialized.")

    def depends_openai_client(
        self,
        request: Request,
        api_type: Optional[Text] = Query(None),
        org: Optional[Text] = Query(None),
        org_type: Optional[Text] = Query(None),
        organization: Optional[Text] = Query(None),
        organization_type: Optional[Text] = Query(None),
        body: Optional[Any] = Body(None),
    ) -> "OpenAI":
        """Returns the OpenAI client based on the request parameters."""

        logger = get_value_from_app(
            request.app, key="logger", value_typing=Logger, default=languru_logger
        )

        # Parse request parameters
        organization_type = (
            organization_type or organization or org_type or org or api_type
        )
        if organization_type is None:
            model = str(body["model"]) if body and "model" in body else None
            if model and "/" in model:
                might_org = model.split("/")[0]
                try:
                    organization_type = to_org_type(might_org)
                except OrganizationNotFound:
                    pass
        else:
            organization_type = to_org_type(organization_type)

        # Try search supported models
        model = str(body["model"]) if body and "model" in body else None
        if model is not None:
            for _c in (
                self._oai_client,
                self._aoai_client,
                self._ant_client,
                self._gg_client,
                self._gq_client,
                self._pplx_client,
                self._vg_client,
            ):
                if _c is None:
                    continue
                if hasattr(_c, "models") and hasattr(_c.models, "supported_models"):
                    if model in _c.models.supported_models:  # type: ignore
                        return _c

        # Return the OpenAI client based on the organization_type
        if organization_type is None:
            logger.warning("No organization type specified. Using OpenAI by default.")
            if self._oai_client is None:
                raise OrganizationNotFound("OpenAI client not initialized.")
            else:
                _client = self._oai_client
        else:
            _client = self._org_to_openai_client(organization_type)
        return _client

    def _org_to_openai_client(
        self, org: Union[Text, "OrganizationType", Any]
    ) -> "OpenAI":
        """Returns the OpenAI client based on the organization type."""

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


openai_clients = OpenaiClients()
