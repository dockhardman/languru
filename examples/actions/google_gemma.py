from typing import Text

from languru.action.base import ModelDeploy
from languru.action.hf import TransformersAction


class GoogleGemmaAction(TransformersAction):
    # Model configuration
    MODEL_NAME = "google/gemma-2b-it"
    # google/gemma-7b-it, google/gemma-7b, google/gemma-2b-it, google/gemma-2b

    model_deploys = (
        ModelDeploy("microsoft/phi-1_5", "microsoft/phi-1_5"),
        ModelDeploy("phi-1_5", "microsoft/phi-1_5"),
    )

    def name(self) -> Text:
        return "google_gemma_action"

    def health(self) -> bool:
        return True
