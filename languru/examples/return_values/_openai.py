import random
import time

from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.create_embedding_response import CreateEmbeddingResponse

from languru.types.completions import Completion
from languru.types.model import Model

return_chat_completion = ChatCompletion.model_validate(
    {
        "id": "chatcmpl-xxxxxxxxxxxxxxxxxxxxxxxx",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": "Hello! How can I assist you today?",
                    "role": "assistant",
                },
            }
        ],
        "created": 1710559936,
        "model": "gpt-3.5-turbo-0125",
        "object": "chat.completion",
        "system_fingerprint": "fp_xxxxxxxx",
        "usage": {
            "completion_tokens": 9,
            "prompt_tokens": 19,
            "total_tokens": 28,
        },
    }
)
return_chat_completion_chunks = [
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": "", "role": "assistant"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": "Hello"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": "!"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": " How"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": " can"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": " I"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": " assist"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": " you"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": " today"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {"content": "?"}, "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
    ChatCompletionChunk.model_validate(
        {
            "id": "chatcmpl-xxxx",
            "choices": [{"delta": {}, "finish_reason": "stop", "index": 0}],
            "created": 1710565261,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion.chunk",
            "system_fingerprint": "fp_xxxx",
        }
    ),
]
return_text_completion = Completion.model_validate(
    {
        "id": "cmpl-xxxxxxxxxxxxxxxxxxxx",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "text": "\n\nThis is a test.",
            }
        ],
        "created": 1710579700,
        "model": "gpt-3.5-turbo-instruct",
        "object": "text_completion",
        "usage": {"completion_tokens": 6, "prompt_tokens": 5, "total_tokens": 11},
    }
)
return_text_completion_stream = [
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": None, "index": 0, "logprobs": None, "text": "\n\n"}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": None, "index": 0, "logprobs": None, "text": "This"}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": None, "index": 0, "logprobs": None, "text": " is"}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": None, "index": 0, "logprobs": None, "text": " a"}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": None, "index": 0, "logprobs": None, "text": " test"}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": None, "index": 0, "logprobs": None, "text": "."}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
    Completion.model_validate(
        {
            "id": "cmpl-xxxxxxxxx",
            "choices": [
                {"finish_reason": "stop", "index": 0, "logprobs": None, "text": ""}
            ],
            "created": 1710580063,
            "model": "gpt-3.5-turbo-instruct",
            "object": "text_completion",
        }
    ),
]
return_embedding = CreateEmbeddingResponse.model_validate(
    {
        "data": [
            {
                "embedding": [random.uniform(-1, 1) for _ in range(1536)],
                "index": 0,
                "object": "embedding",
            },
            {
                "embedding": [random.uniform(-1, 1) for _ in range(1536)],
                "index": 1,
                "object": "embedding",
            },
        ],
        "model": "text-embedding-ada-002",
        "object": "list",
        "usage": {"prompt_tokens": 3, "total_tokens": 3},
    }
)
return_model = Model.model_validate(
    {
        "id": "model_id",
        "created": int(time.time()),
        "object": "model",
        "owned_by": "test",
    }
)
return_moderation_create = {
    "id": "modr-xxxxxxxx",
    "model": "text-moderation-007",
    "results": [
        {
            "categories": {
                "harassment": True,
                "harassment/threatening": True,
                "hate": False,
                "hate/threatening": False,
                "self-harm": False,
                "self-harm/instructions": False,
                "self-harm/intent": False,
                "sexual": False,
                "sexual/minors": False,
                "violence": True,
                "violence/graphic": False,
            },
            "category_scores": {
                "harassment": 0.5289425849914551,
                "harassment/threatening": 0.5736028552055359,
                "hate": 0.2289084941148758,
                "hate/threatening": 0.02360980585217476,
                "self-harm": 2.2852241272630636e-06,
                "self-harm/instructions": 1.1107282871236634e-09,
                "self-harm/intent": 1.6410396028732066e-06,
                "sexual": 1.223516846948769e-05,
                "sexual/minors": 7.491369302670137e-08,
                "violence": 0.9972043633460999,
                "violence/graphic": 3.43257597705815e-05,
            },
            "flagged": True,
        }
    ],
}
