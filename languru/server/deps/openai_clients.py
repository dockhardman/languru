from logging import Logger
from typing import Any, Optional, Text, Union

from fastapi import Body, Query, Request
from openai import AzureOpenAI, OpenAI

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
    def __init__(self):
        self._oai_client = OpenAI()
        self._aoai_client = AzureOpenAI()
        self._ant_client = AnthropicOpenAI()
        self._gg_client = GoogleOpenAI()
        self._gq_client = GroqOpenAI()
        self._pplx_client = PerplexityOpenAI()
        self._vg_client = VoyageOpenAI()

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
                if hasattr(_c, "models") and hasattr(_c.models, "supported_models"):
                    if model in _c.models.supported_models:  # type: ignore
                        return _c

        # Return the OpenAI client based on the organization_type
        _client = self._oai_client
        if organization_type is None:
            logger.warning("No organization type specified. Using OpenAI by default.")
        else:
            _client = self._org_to_openai_client(organization_type)
        return _client

    def _org_to_openai_client(
        self, org: Union[Text, "OrganizationType", Any]
    ) -> "OpenAI":
        """Returns the OpenAI client based on the organization type."""

        org = to_org_type(org)
        if org == OrganizationType.OPENAI:
            return self._oai_client
        if org == OrganizationType.AZURE:
            return self._aoai_client
        if org == OrganizationType.ANTHROPIC:
            return self._ant_client
        if org == OrganizationType.GOOGLE:
            return self._gg_client
        if org == OrganizationType.GROQ:
            return self._gq_client
        if org == OrganizationType.PERPLEXITY:
            return self._pplx_client
        if org == OrganizationType.VOYAGE:
            return self._vg_client
        raise OrganizationNotFound(f"Unknown organization: '{org}'.")
