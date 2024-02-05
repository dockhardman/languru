from functools import lru_cache
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Text, Tuple

if TYPE_CHECKING:
    from openai.types import Completion, CreateEmbeddingResponse
    from openai.types.chat import ChatCompletion, ChatCompletionMessageParam


ModelDeploy = NamedTuple(
    "ModelDeploy", [("model_deploy_name", Text), ("model_name", Text)]
)


class ActionBase:
    model_deploys: Optional[Tuple[ModelDeploy, ...]] = None

    def __init__(
        self, *args, model_deploys: Optional[Tuple[ModelDeploy]] = None, **kwargs
    ):
        self._model_deploys = (
            self.model_deploys if model_deploys is None else model_deploys
        )

    def name(self) -> Text:
        raise NotImplementedError

    def health(self) -> bool:
        raise NotImplementedError

    def chat(
        self, message: List["ChatCompletionMessageParam"], **kwargs
    ) -> "ChatCompletion":
        raise NotImplementedError

    def text_completion(self, prompt: Text, **kwargs) -> "Completion":
        raise NotImplementedError

    def embeddings(self, input: Text, **kwargs) -> "CreateEmbeddingResponse":
        raise NotImplementedError

    @lru_cache
    def get_model_name(self, model_deploy_name: Text) -> Text:
        for model_deploy in self._model_deploys:
            if model_deploy.model_deploy_name == model_deploy_name:
                return model_deploy.model_name
        raise ValueError(f"Model deploy {model_deploy_name} not found")
