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
