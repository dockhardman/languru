from typing import cast

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pyassorted.asyncio.executor import run_generator

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.deps.common import app_settings
from languru.server.utils.common import get_value_from_app
from languru.types.audio import AudioSpeechRequest

router = APIRouter()


class AudioSpeechHandler:

    async def handle_request(
        self,
        request: "Request",
        audio_speech_request: "AudioSpeechRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> StreamingResponse:
        if settings.APP_TYPE == AppType.llm:
            settings = cast(LlmSettings, settings)
            return await self.handle_llm(
                request=request,
                audio_speech_request=audio_speech_request,
                settings=settings,
                **kwargs,
            )

        if settings.APP_TYPE == AppType.agent:
            settings = cast(AgentSettings, settings)
            return await self.handle_agent(
                request=request,
                audio_speech_request=audio_speech_request,
                settings=settings,
                **kwargs,
            )

        # Not implemented or unknown app server type
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unknown app server type: {settings.APP_TYPE}"
                if settings.APP_TYPE
                else "App server type not implemented"
            ),
        )

    async def handle_llm(
        self,
        request: "Request",
        audio_speech_request: "AudioSpeechRequest",
        settings: "LlmSettings",
        **kwargs,
    ) -> StreamingResponse:
        from languru.action.base import ActionBase

        action: "ActionBase" = get_value_from_app(
            request.app, key="action", value_typing=ActionBase
        )

        try:
            audio_speech_request.model = action.get_model_name(
                audio_speech_request.model
            )
        except ModelNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        return StreamingResponse(
            run_generator(
                action.audio_speech,
                **audio_speech_request.model_dump(exclude_none=True),
            ),
            media_type="audio/mpeg",
        )

    async def handle_agent(
        self,
        request: "Request",
        audio_speech_request: "AudioSpeechRequest",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> StreamingResponse: ...


@router.post("/audio/speech")
async def audio_speech(
    request: Request,
    audio_speech_request: AudioSpeechRequest = Body(
        ...,
        openapi_examples={
            "OpenAI": {
                "summary": "OpenAI",
                "description": "Chat completion request",
                "value": {
                    "model": "tts-1",
                    "voice": "alloy",
                    "input": "The quick brown fox jumped over the lazy dog.",
                },
            },
        },
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> StreamingResponse:
    return await AudioSpeechHandler().handle_request(
        request=request,
        audio_speech_request=audio_speech_request,
        settings=settings,
    )
