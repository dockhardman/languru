from typing import Text

from fastapi import APIRouter, Body, Depends, File, Form, Request, UploadFile
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.audio import Transcription, Translation
from pyassorted.asyncio.executor import run_func, run_generator

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients
from languru.types.audio import (
    AudioSpeechRequest,
    AudioTranscriptionRequest,
    AudioTranslationRequest,
)

router = APIRouter()


class AudioSpeechHandler:
    async def handle_request(
        self,
        request: "Request",
        *args,
        audio_speech_request: "AudioSpeechRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> StreamingResponse:
        # Request audio speech
        with openai_client.audio.speech.with_streaming_response.create(
            **audio_speech_request.model_dump(exclude_none=True)
        ) as response:
            return StreamingResponse(
                run_generator(response.iter_bytes),  # type: ignore
                media_type="audio/mpeg",
            )


class AudioTranscriptionHandler:
    async def handle_request(
        self,
        request: "Request",
        audio_transcription_request: "AudioTranscriptionRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> Transcription:
        return await run_func(
            openai_client.audio.transcriptions.create,
            **audio_transcription_request.model_dump(exclude_none=True),
        )


class AudioTranslationHandler:
    async def handle_request(
        self,
        request: "Request",
        audio_translation_request: "AudioTranslationRequest",
        openai_client: "OpenAI",
        settings: "ServerBaseSettings",
        **kwargs,
    ) -> Translation:
        return await run_func(
            openai_client.audio.translations.create,
            **audio_translation_request.model_dump(exclude_none=True),
        )


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
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> StreamingResponse:
    return await AudioSpeechHandler().handle_request(
        request=request,
        audio_speech_request=audio_speech_request,
        openai_client=openai_client,
        settings=settings,
    )


@router.post("/audio/transcriptions")
async def audio_transcriptions(
    request: Request,
    file: UploadFile = File(...),
    model: Text = Form(...),
    language: Text = Form(None),
    prompt: Text = Form(None),
    response_format: Text = Form(None),
    temperature: float = Form(None),
    timestamp_granularities: Text = Form(None),
    timeout: float = Form(None),
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Transcription:
    return await AudioTranscriptionHandler().handle_request(
        request=request,
        audio_transcription_request=AudioTranscriptionRequest.model_validate(
            {
                "file": await file.read(),
                "model": model,
                "language": language,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
                "timestamp_granularities": timestamp_granularities,
                "timeout": timeout,
            }
        ),
        openai_client=openai_client,
        settings=settings,
    )


@router.post("/audio/translations")
async def audio_translations(
    request: Request,
    file: UploadFile = File(...),
    model: Text = Form(...),
    language: Text = Form(None),
    prompt: Text = Form(None),
    response_format: Text = Form(None),
    temperature: float = Form(None),
    timeout: float = Form(None),
    openai_client=Depends(openai_clients.depends_openai_client),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Translation:
    return await AudioTranslationHandler().handle_request(
        request=request,
        audio_translation_request=AudioTranslationRequest.model_validate(
            {
                "file": await file.read(),
                "model": model,
                "language": language,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
                "timeout": timeout,
            }
        ),
        openai_client=openai_client,
        settings=settings,
    )
