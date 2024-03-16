import os
from typing import Optional, Text

import openai

from languru.action.base import ModelDeploy
from languru.action.openai import OpenaiAction
from languru.config import logger


class GroqAction(OpenaiAction):
    model_deploys = (
        ModelDeploy("llama2-70b-4096", "llama2-70b-4096"),
        ModelDeploy("mixtral-8x7b-32768", "mixtral-8x7b-32768"),
    )

    def __init__(
        self,
        *args,
        api_key: Optional[Text] = None,
        **kwargs,
    ):
        from groq import Groq

        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if api_key is None:
            logger.error("GROQ_API_KEY is not set")
        self._client = Groq(api_key=api_key)

    def name(self):
        return "groq_action"

    def health(self) -> bool:
        try:
            self._client.models.retrieve(model="mixtral-8x7b-32768")
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class GroqOpenaiAction(OpenaiAction):
    model_deploys = (
        ModelDeploy("llama2-70b-4096", "llama2-70b-4096"),
        ModelDeploy("mixtral-8x7b-32768", "mixtral-8x7b-32768"),
    )

    def __init__(
        self,
        *args,
        api_key: Optional[Text] = None,
        **kwargs,
    ):
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if api_key is None:
            logger.error("GROQ_API_KEY is not set")
        self._client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1", api_key=api_key
        )

    def name(self):
        return "groq_openai_action"

    def health(self) -> bool:
        try:
            self._client.models.retrieve(model="mixtral-8x7b-32768")
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
