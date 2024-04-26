from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class TextToSpeechRequest(BaseModel):
    input: str = Field(
        ...,
        description=(
            "The text to generate audio for. The maximum length is 4096 characters."
        ),
    )
    model: Union[str, Literal["tts-1", "tts-1-hd"]] = Field(
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
    timeout: Optional[Union[float, str]] = Field(
        None,
        description=(
            "Override the client-level default timeout for this request, in seconds."
        ),
    )
