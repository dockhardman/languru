import time

from fastapi import APIRouter, Body, Request
from openai.types.chat.chat_completion import ChatCompletion

from languru.types.chat.completions import ChatCompletionRequest

router = APIRouter()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    chat_completions_create: ChatCompletionRequest = Body(
        ...,
        example={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        },
    ),
) -> ChatCompletion:
    print(chat_completions_create)
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo-0613",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "\n\nHello there, how may I assist you today?",
                },
                "logprobs": None,
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21},
    }
