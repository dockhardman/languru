from typing import TYPE_CHECKING, List, Optional, Text, Union

import google.generativeai as genai

from languru.action.base import ActionBase, ModelDeploy
from languru.llm.config import logger

if TYPE_CHECKING:
    from openai.types import Completion, CreateEmbeddingResponse
    from openai.types.chat import ChatCompletion, ChatCompletionMessageParam


class GoogleGenAiAction(ActionBase):
    model_deploys = (
        ModelDeploy("models/chat-bison-001", "models/chat-bison-001"),
        ModelDeploy("models/text-bison-001", "models/text-bison-001"),
        ModelDeploy("models/embedding-gecko-001", "models/embedding-gecko-001"),
        ModelDeploy("models/gemini-1.0-pro", "models/gemini-1.0-pro"),
        ModelDeploy("models/gemini-1.0-pro-001", "models/gemini-1.0-pro-001"),
        ModelDeploy("models/gemini-1.0-pro-latest", "models/gemini-1.0-pro-latest"),
        ModelDeploy(
            "models/gemini-1.0-pro-vision-latest", "models/gemini-1.0-pro-vision-latest"
        ),
        ModelDeploy("models/gemini-pro", "models/gemini-pro"),
        ModelDeploy("models/gemini-pro-vision", "models/gemini-pro-vision"),
        ModelDeploy("models/embedding-001", "models/embedding-001"),
        ModelDeploy("models/aqa", "models/aqa"),
        ModelDeploy("chat-bison-001", "models/chat-bison-001"),
        ModelDeploy("text-bison-001", "models/text-bison-001"),
        ModelDeploy("embedding-gecko-001", "models/embedding-gecko-001"),
        ModelDeploy("gemini-1.0-pro", "models/gemini-1.0-pro"),
        ModelDeploy("gemini-1.0-pro-001", "models/gemini-1.0-pro-001"),
        ModelDeploy("gemini-1.0-pro-latest", "models/gemini-1.0-pro-latest"),
        ModelDeploy(
            "gemini-1.0-pro-vision-latest", "models/gemini-1.0-pro-vision-latest"
        ),
        ModelDeploy("gemini-pro", "models/gemini-pro"),
        ModelDeploy("gemini-pro-vision", "models/gemini-pro-vision"),
        ModelDeploy("embedding-001", "models/embedding-001"),
        ModelDeploy("aqa", "models/aqa"),
    )

    def __init__(
        self,
        *args,
        api_key: Optional[Text] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        genai.configure(api_key=api_key)

    def name(self) -> Text:
        raise NotImplementedError

    def health(self) -> bool:
        raise NotImplementedError

    def chat(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> "ChatCompletion":
        raise NotImplementedError

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        raise NotImplementedError

    def embeddings(
        self,
        input: Union[Text, List[Union[Text, List[Text]]]],
        *args,
        model: Text,
        **kwargs,
    ) -> "CreateEmbeddingResponse":
        raise NotImplementedError
