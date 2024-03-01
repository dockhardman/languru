from typing import Optional, Text

import openai

from languru.action.base import ModelDeploy
from languru.action.openai import OpenaiAction


class PerplexityAction(OpenaiAction):
    model_deploys = (
        ModelDeploy("sonar-small-chat", "sonar-small-chat"),
        ModelDeploy("sonar-small-online", "sonar-small-online"),
        ModelDeploy("sonar-medium-chat", "sonar-medium-chat"),
        ModelDeploy("sonar-medium-online", "sonar-medium-online"),
        ModelDeploy("codellama-34b-instruct", "codellama-34b-instruct"),
        ModelDeploy("codellama-70b-instruct", "codellama-70b-instruct"),
        ModelDeploy("llama-2-70b-chat", "llama-2-70b-chat"),
        ModelDeploy("mistral-7b-instruct", "mistral-7b-instruct"),
        ModelDeploy("mixtral-8x7b-instruct", "mixtral-8x7b-instruct"),
        ModelDeploy("pplx-7b-chat", "pplx-7b-chat"),
        ModelDeploy("pplx-7b-online", "pplx-7b-online"),
        ModelDeploy("pplx-70b-chat", "pplx-70b-chat"),
        ModelDeploy("pplx-70b-online", "pplx-70b-online"),
    )

    def __init__(
        self,
        *args,
        api_key: Optional[Text] = None,
        base_url: Text = "https://api.perplexity.ai",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def name(self):
        return "perplexity_action"

    def health(self) -> bool:
        return True  # Wait Perplexity API update
