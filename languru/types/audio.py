from typing import List, Literal, Optional, Text, Union

from openai._types import FileTypes
from pydantic import BaseModel, Field


class TextToSpeechRequest(BaseModel):
    input: Text = Field(
        ...,
        description=(
            "The text to generate audio for. The maximum length is 4096 characters."
        ),
    )
    model: Union[Text, Literal["tts-1", "tts-1-hd"]] = Field(
        ..., description="One of the available TTS models: `tts-1` or `tts-1-hd`."
    )
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = Field(
        ..., description="The voice to use when generating the audio."
    )
    response_format: Optional[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]] = (
        Field(
            None,
            description=(
                "The format to return the audio in. Supported formats are "
                + "`mp3`, `opus`, `aac`, `flac`, `wav`, and `pcm`."
            ),
        )
    )
    speed: Optional[float] = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description=(
            "The speed of the generated audio. Select a value from "
            + "`0.25` to `4.0`. `1.0` is the default."
        ),
    )
    timeout: Optional[float] = Field(
        None,
        description=(
            "Override the client-level default timeout for this request, in seconds."
        ),
    )


class TranscriptionCreateRequest(BaseModel):
    file: FileTypes = Field(...)
    model: Union[Text, Literal["whisper-1"]]
    language: Optional[Text] = None
    prompt: Optional[Text] = None
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = (
        None
    )
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = None
    timeout: Optional[float] = None
