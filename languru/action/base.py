from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Generator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Text,
    Union,
)

from languru.exceptions import ModelNotFound

if TYPE_CHECKING:
    from openai.types import (
        Completion,
        CreateEmbeddingResponse,
        ModerationCreateResponse,
    )
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionMessageParam,
    )


ModelDeploy = NamedTuple(
    "ModelDeploy", [("model_deploy_name", Text), ("model_name", Text)]
)


class ActionBase:
    model_deploys: Optional[Sequence[ModelDeploy]] = None

    default_max_tokens: int = 800

    def __init__(
        self, *args, model_deploys: Optional[Sequence[ModelDeploy]] = None, **kwargs
    ):
        self._model_deploys = (
            self.model_deploys if model_deploys is None else model_deploys
        ) or ()

    def name(self) -> Text:
        raise NotImplementedError

    def health(self) -> bool:
        raise NotImplementedError

    def chat(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> "ChatCompletion":
        raise NotImplementedError

    def chat_stream(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator["ChatCompletionChunk", None, None]:
        raise NotImplementedError

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        raise NotImplementedError

    def text_completion_stream(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> Generator["Completion", None, None]:
        raise NotImplementedError

    def embeddings(
        self,
        input: Union[Text, List[Union[Text, List[Text]]]],
        *args,
        model: Text,
        **kwargs,
    ) -> "CreateEmbeddingResponse":
        raise NotImplementedError

    def moderations(
        self, input: Text, *args, model: Text, **kwargs
    ) -> "ModerationCreateResponse":
        raise NotImplementedError

    @lru_cache
    def get_model_name(self, model_deploy_name: Text) -> Text:
        for model_deploy in self._model_deploys:
            if model_deploy.model_deploy_name == model_deploy_name:
                return model_deploy.model_name
        raise ModelNotFound(f"Model deploy {model_deploy_name} not found")

    def chat_stream_sse(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator[Text, None, None]:
        for chat in self.chat_stream(messages, model=model, **kwargs):
            yield f"data: {chat.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
