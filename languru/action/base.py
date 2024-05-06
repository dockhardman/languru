import time
from abc import ABC
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Text,
    Union,
)

from rich.console import Console
from rich.prompt import Prompt

from languru.config import console as languru_console
from languru.exceptions import ModelNotFound
from languru.utils.common import str_strong_casefold

if TYPE_CHECKING:
    from openai._types import FileTypes
    from openai.types import (
        Completion,
        CreateEmbeddingResponse,
        ImagesResponse,
        ModerationCreateResponse,
    )
    from openai.types.audio import Transcription, Translation
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionMessageParam,
    )


ModelDeploy = NamedTuple(
    "ModelDeploy", [("model_deploy_name", Text), ("model_name", Text)]
)


def chat_interactive(
    action: "ActionBase",
    *,
    model: Text,
    console: Optional["Console"] = None,
    max_tokens: int = 200,
) -> None:
    console = console or languru_console

    messages: List[Dict] = []
    while True:
        user_says = Prompt.ask("User", console=console).strip()
        if not user_says:
            continue
        if user_says.casefold() in ("exit", "quit", "q"):
            break
        console.print()

        # Chat
        messages.append({"role": "user", "content": user_says})
        chat_params = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        chat_start = time.time()
        chat_res = action.chat(**chat_params)
        chat_timecost = time.time() - chat_start
        assert len(chat_res.choices) > 0 and chat_res.choices[0].message.content
        assistant_says = chat_res.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_says})
        console.print(f"Assistant: {assistant_says}")
        console.print()

        # Tokens per second
        res_total_tokens = (
            0.0 if chat_res.usage is None else chat_res.usage.total_tokens
        )
        console.print(
            f"{res_total_tokens / chat_timecost:.3f} tokens/s", style="italic blue"
        )


class ActionText(ABC):
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


class ActionAudio(ABC):
    def audio_speech(
        self, input: Text, *args, model: Text, voice: Text, **kwargs
    ) -> Generator[bytes, None, None]:
        raise NotImplementedError

    def audio_transcriptions(
        self, file: "FileTypes", *args, model: Text, **kwargs
    ) -> "Transcription":
        raise NotImplementedError

    def audio_translations(
        self, file: "FileTypes", *args, model: Text, **kwargs
    ) -> "Translation":
        raise NotImplementedError


class ActionImage(ABC):
    def images_generations(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "ImagesResponse":
        raise NotImplementedError

    def images_edits(
        self, image: "FileTypes", *args, model: Text, **kwargs
    ) -> "ImagesResponse":
        raise NotImplementedError

    def images_variations(
        self, image: "FileTypes", *args, model: Text, **kwargs
    ) -> "ImagesResponse":
        raise NotImplementedError


class ActionBase(ActionText, ActionAudio, ActionImage):
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
