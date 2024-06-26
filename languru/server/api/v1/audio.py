from typing import Optional, Text, Tuple

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
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
from languru.types.organizations import OrganizationType
from languru.utils.common import dummy_generator_func

router = APIRouter()


def depends_openai_client_model(
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    model: Text = Form(...),
) -> Tuple[OpenAI, Text]:
    if org_type is None:
        org_type = openai_clients.org_from_model(model)

    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")
    else:
        openai_client = openai_clients.org_to_openai_client(org_type)
        return (openai_client, model)


def depends_openai_client_audio_speech_request(
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
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
) -> Tuple[OpenAI, AudioSpeechRequest]:
    if org_type is None:
        org_type = openai_clients.org_from_model(audio_speech_request.model)

    if org_type is None:
        raise HTTPException(status_code=400, detail="Organization type not found.")
    else:
        openai_client = openai_clients.org_to_openai_client(org_type)
        return (openai_client, audio_speech_request)


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
                run_generator(dummy_generator_func(response.iter_bytes())),
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
    openai_client_audio_speech_request: Tuple[OpenAI, AudioSpeechRequest] = Depends(
        depends_openai_client_audio_speech_request
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> StreamingResponse:
    return await AudioSpeechHandler().handle_request(
        request=request,
        audio_speech_request=openai_client_audio_speech_request[1],
        openai_client=openai_client_audio_speech_request[0],
        settings=settings,
    )


@router.post("/audio/transcriptions")
async def audio_transcriptions(
    request: Request,
    file: UploadFile = File(...),
    language: Text = Form(None),
    prompt: Text = Form(None),
    response_format: Text = Form(None),
    temperature: float = Form(None),
    timestamp_granularities: Text = Form(None),
    timeout: float = Form(None),
    openai_client_model: Tuple[OpenAI, Text] = Depends(depends_openai_client_model),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Transcription:
    return await AudioTranscriptionHandler().handle_request(
        request=request,
        audio_transcription_request=AudioTranscriptionRequest.model_validate(
            {
                "file": await file.read(),
                "model": openai_client_model[1],
                "language": language,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
                "timestamp_granularities": timestamp_granularities,
                "timeout": timeout,
            }
        ),
        openai_client=openai_client_model[0],
        settings=settings,
    )


@router.post("/audio/translations")
async def audio_translations(
    request: Request,
    file: UploadFile = File(...),
    language: Text = Form(None),
    prompt: Text = Form(None),
    response_format: Text = Form(None),
    temperature: float = Form(None),
    timeout: float = Form(None),
    openai_client_model: Tuple[OpenAI, Text] = Depends(depends_openai_client_model),
    settings: ServerBaseSettings = Depends(app_settings),
) -> Translation:
    return await AudioTranslationHandler().handle_request(
        request=request,
        audio_translation_request=AudioTranslationRequest.model_validate(
            {
                "file": await file.read(),
                "model": openai_client_model[1],
                "language": language,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
                "timeout": timeout,
            }
        ),
        openai_client=openai_client_model[0],
        settings=settings,
    )
