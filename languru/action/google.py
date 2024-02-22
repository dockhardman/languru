import time
import uuid
from typing import TYPE_CHECKING, List, Optional, Text, Union

import google.generativeai as genai
from google.generativeai.types.content_types import ContentDict
from google.generativeai.types.text_types import BatchEmbeddingDict
from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletion
from openai.types.completion import Completion

from languru.action.base import ActionBase, ModelDeploy
from languru.llm.config import logger

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


class GoogleGenaiAction(ActionBase):
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
        return "google_genai_action"

    def health(self) -> bool:
        try:
            genai.get_model("models/gemini-pro")
            return True
        except Exception as e:
            logger.error(f"Google GenAI health check failed: {e}")
            return False

    def chat(
        self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs
    ) -> "ChatCompletion":
        if len(messages) == 0:
            raise ValueError("messages must not be empty")

        # pop out the last message
        genai_model = genai.GenerativeModel(model)
        contents: List[ContentDict] = [
            ContentDict(role=m["role"], parts=[m["content"]])
            for m in messages
            if "content" in m and m["content"]
        ]
        input_tokens = genai_model.count_tokens(contents).total_tokens

        # Generate the chat response
        latest_content = contents.pop()
        chat_session = genai_model.start_chat(history=contents or None)
        response = chat_session.send_message(latest_content)
        out_tokens = genai_model.count_tokens(response.parts).total_tokens

        # Parse the response
        chat_completion = ChatCompletion.model_validate(
            dict(
                id=str(uuid.uuid4()),
                choices=[
                    dict(
                        finish_reason="stop",
                        index=idx,
                        message=dict(content=part.text, role="assistant"),
                    )
                    for idx, part in enumerate(response.parts)
                    if part.text
                ],
                created=int(time.time()),
                model=model,
                object="chat.completion",
                usage=dict(
                    completion_tokens=out_tokens,
                    prompt_tokens=input_tokens,
                    total_tokens=input_tokens + out_tokens,
                ),
            )
        )
        return chat_completion

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        if not prompt:
            raise ValueError("prompt must not be empty")
        genai_model = genai.GenerativeModel(model)
        input_tokens = genai_model.count_tokens(prompt).total_tokens

        # Generate the text
        gen_res = genai_model.generate_content(prompt)
        output_tokens = genai_model.count_tokens(gen_res.parts).total_tokens

        # Parse the response
        completion_res = Completion.model_validate(
            dict(
                id=str(uuid.uuid4()),
                choices=[
                    dict(
                        finish_reason="stop",
                        index=idx,
                        text=part.text,
                    )
                    for idx, part in enumerate(gen_res.parts)
                    if part.text
                ],
                created=int(time.time()),
                model=model,
                object="text_completion",
                usage=dict(
                    completion_tokens=output_tokens,
                    prompt_tokens=input_tokens,
                    total_tokens=input_tokens + output_tokens,
                ),
            )
        )
        return completion_res

    def embeddings(
        self,
        input: Union[Text, List[Union[Text, List[Text]]]],
        *args,
        model: Text,
        **kwargs,
    ) -> "CreateEmbeddingResponse":
        if not input:
            raise ValueError("The input must not be empty")
        contents: List[Text] = []
        if isinstance(input, List):
            for idx, seq in enumerate(input):
                if not seq:
                    raise ValueError(f"The input[{idx}] must not be empty")
                elif isinstance(seq, Text):
                    contents.append(seq)
                else:
                    contents.append("".join(seq))
        else:
            contents.append(input)
        input_tokens = (
            genai.GenerativeModel("models/gemini-pro")
            .count_tokens(contents)
            .total_tokens
        )

        # Retrieve the embeddings
        batch_emb_dict: BatchEmbeddingDict = genai.embed_content(
            model=model,
            content=contents,
            task_type="retrieval_document",
        )

        # Parse the response
        emb_res = CreateEmbeddingResponse.model_validate(
            dict(
                data=[
                    dict(
                        embedding=emb,
                        index=idx,
                        object="embedding",
                    )
                    for idx, emb in enumerate(batch_emb_dict["embedding"])
                ],
                model=model,
                object="list",
                usage=dict(prompt_tokens=input_tokens, total_tokens=input_tokens),
            )
        )
        return emb_res
