from openai.types.chat import ChatCompletion, ChatCompletionChunk

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
