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
from languru.utils.common import str_strong_casefold

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

    default_max_tokens: int = 20

    def __init__(
        self, *args, model_deploys: Optional[Sequence[ModelDeploy]] = None, **kwargs
    ):
        self._model_deploys = (
            self.model_deploys if model_deploys is None else model_deploys
        ) or ()

    @classmethod
    def from_models(
        cls,
        model_deploys: Optional[Sequence[ModelDeploy]] = None,
        model: Optional[Text] = None,
        model_name: Optional[Text] = None,
        **kwargs,
    ):
        model_name = model_name or model
        model_deploys = list(model_deploys or [])
        if model_name:
            model_deploys.append(ModelDeploy(model_name, model_name))
            model_deploys.append(ModelDeploy(model_name.split("/")[-1], model_name))
        if model_deploys:
            model_deploys = tuple(sorted(list(set(model_deploys)), key=lambda x: x[0]))
        return cls(
            model_deploys=model_deploys or None,
            model_name=model_name or None,
            model=model_name or None,
            **kwargs,
        )

    def name(self) -> Text:
        raise NotImplementedError  # pragma: no cover

    def health(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    def chat(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> "ChatCompletion":
        raise NotImplementedError  # pragma: no cover

    def chat_stream(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator["ChatCompletionChunk", None, None]:
        raise NotImplementedError  # pragma: no cover

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        raise NotImplementedError  # pragma: no cover

    def text_completion_stream(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> Generator["Completion", None, None]:
        raise NotImplementedError  # pragma: no cover

    def embeddings(
        self, input: Union[Text, List[Text]], *args, model: Text, **kwargs
    ) -> "CreateEmbeddingResponse":
        raise NotImplementedError  # pragma: no cover

    def moderations(
        self, input: Text, *args, model: Text, **kwargs
    ) -> "ModerationCreateResponse":
        raise NotImplementedError  # pragma: no cover

    @lru_cache
    def get_model_name(self, model_deploy_name: Text) -> Text:
        for model_deploy in self._model_deploys:
            if model_deploy.model_deploy_name == model_deploy_name:
                return model_deploy.model_name
        raise ModelNotFound(f"Model deploy {model_deploy_name} not found")

    @lru_cache
    def validate_model(self, model: Text, **kwargs) -> Text:
        if self.model_deploys is None:
            raise ModelNotFound(
                f"No model deploys are defined in {self.__class__.__name__}"
            )
        for model_deploy in self.model_deploys:
            if model_deploy.model_name == model:
                return model_deploy.model_name
            elif model_deploy.model_deploy_name == model:
                return model_deploy.model_name
            elif str_strong_casefold(model_deploy.model_name) == str_strong_casefold(
                model
            ):
                return model_deploy.model_name
            elif str_strong_casefold(
                model_deploy.model_deploy_name
            ) == str_strong_casefold(model):
                return model_deploy.model_name
        raise ModelNotFound(f"Model deploy {model} not found")

    def chat_stream_sse(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> Generator[Text, None, None]:
        for chat in self.chat_stream(messages, model=model, **kwargs):
            yield f"data: {chat.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    def text_completion_stream_sse(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> Generator[Text, None, None]:
        for completion in self.text_completion_stream(prompt, model=model, **kwargs):
            yield f"data: {completion.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
