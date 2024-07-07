import os
import time
from typing import Optional, Text

import httpx
import openai
from openai import OpenAI
from openai import resources as OpenAIResources
from openai._types import NOT_GIVEN, Body, Headers, NotGiven, Query
from openai.pagination import SyncPage
from openai.types.model import Model

from languru.exceptions import CredentialsNotProvided
from languru.openai_plugins.clients.utils import openai_init_parameter_keys
from languru.types.models import MODELS_PERPLEXITY


class PerplexityModels(OpenAIResources.Models):

    supported_models = frozenset(MODELS_PERPLEXITY)
    temperature_span = (0.0, 1.99)

    def retrieve(
        self,
        model: str,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> "Model":
        if model in self.supported_models:
            return Model.model_validate(
                {
                    "id": model,
                    "created": int(time.time()),
                    "object": "model",
                    "owned_by": "perplexity",
                }
            )
        else:
            error_message = (
                f"Model {model} not found. Supported models are {self.supported_models}"
            )
            raise openai.NotFoundError(
                error_message,
                response=httpx.Response(status_code=404, text=error_message),
                body=None,
            )

    def list(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        **kwargs,
    ) -> "SyncPage[Model]":
        created = int(time.time())
        models = [
            Model.model_validate(
                {
                    "id": model,
                    "created": created,
                    "object": "model",
                    "owned_by": "perplexity",
                }
            )
            for model in self.supported_models
        ]
        return SyncPage(data=models, object="list")


class PerplexityOpenAI(OpenAI):
    models: PerplexityModels

    def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
        api_key = (
            api_key
            or os.getenv("PPLX_API_KEY")
            or os.getenv("PERPLEXITY_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            raise CredentialsNotProvided("Perplexity API key is not provided")
        kwargs["api_key"] = api_key
        kwargs["base_url"] = "https://api.perplexity.ai"
        kwargs = {k: v for k, v in kwargs.items() if k in openai_init_parameter_keys}

        super().__init__(**kwargs)

        self.models = PerplexityModels(self)
