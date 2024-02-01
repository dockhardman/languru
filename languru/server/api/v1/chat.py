from fastapi import APIRouter, Request
from openai.types.chat.chat_completion import ChatCompletion

router = APIRouter()


@router.post("/completions")
async def chat_completions(request: Request) -> ChatCompletion:
    pass
