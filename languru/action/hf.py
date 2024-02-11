import os
from typing import Text

from languru.action.base import ActionBase, ModelDeploy


class TransformersAction(ActionBase):
    MODEL_NAME: Text = (os.getenv("HF_MODEL_NAME") or os.getenv("MODEL_NAME")) or ""
    model_deploys = (ModelDeploy(MODEL_NAME, MODEL_NAME),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._model = None

    def name(self):
        return "transformers_action"
