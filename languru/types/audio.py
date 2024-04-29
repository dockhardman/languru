from typing import Any, Dict, List, Literal, Optional, Text, Union

from openai._types import FileTypes
from pydantic import BaseModel, ConfigDict, Field


class AudioSpeechRequest(BaseModel):
    input: Text = Field(
        ...,
        description=(
            "The text to generate audio for. The maximum length is 4096 characters."
        ),
    )
    model: Union[Text, Literal["tts-1", "tts-1-hd"]] = Field(
        ..., description="One of the available TTS models: `tts-1` or `tts-1-hd`."
    )
    voice: Union[Text, Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = (
        Field(..., description="The voice to use when generating the audio.")
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


class AudioTranscriptionRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: FileTypes = Field(
        ...,
        description=(
            "The audio file object (not file name) to transcribe, in one of these "
            + "formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm."
        ),
    )
    model: Union[Text, Literal["whisper-1"]] = Field(
        ...,
        description=(
            "ID of the model to use. Only `whisper-1` (which is powered by "
            + "our open source Whisper V2 model) is currently available."
        ),
    )
    language: Optional[Text] = Field(
        None,
        description=(
            "The language of the input audio. Supplying the input language in "
            + "[ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) "
            + "format will improve accuracy and latency."
        ),
    )
    prompt: Optional[Text] = Field(
        None,
        description=(
            "An optional text to guide the model's style or continue a previous audio "
            + "segment. The prompt should match the audio language."
        ),
    )
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = (
        Field(
            None,
            description=(
                "The format of the transcript output, in one of these options: "
                + "`json`, `text`, `srt`, `verbose_json`, or `vtt`."
            ),
        )
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description=(
            "The sampling temperature, between 0 and 1. "
            + "Higher values like 0.8 will make the output more random, while "
            + "lower values like 0.2 will make it more focused and deterministic. "
            + "If set to 0, the model will use "
            + "[log probability](https://en.wikipedia.org/wiki/Log_probability) to "
            + "automatically increase the temperature until certain thresholds are hit."
        ),
    )
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = Field(
        None,
        description="The timestamp granularities to populate for this transcription. `response_format` must be set `verbose_json` to use timestamp granularities. Either or both of these options are supported: `word`, or `segment`. Note: There is no additional latency for segment timestamps, but generating word timestamps incurs additional latency.",  # noqa: E501
    )
    timeout: Optional[float] = Field(
        None,
        description=(
            "Override the client-level default timeout for this request, in seconds."
        ),
    )

    def to_files_form(self) -> Dict[Text, Any]:
        out = {
            "file": self.file,
            "model": (None, self.model),
        }
        if self.language is not None:
            out["language"] = (None, self.language)
        if self.prompt is not None:
            out["prompt"] = (None, self.prompt)
        if self.response_format is not None:
            out["response_format"] = (None, self.response_format)
        if self.temperature is not None:
            out["temperature"] = (None, self.temperature)
        if self.timestamp_granularities is not None:
            out["timestamp_granularities"] = (
                None,
                ",".join(self.timestamp_granularities),
            )
        if self.timeout is not None:
            out["timeout"] = (None, self.timeout)
        return out


class AudioTranslationRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: FileTypes = Field(
        ...,
        description=(
            "The audio file object (not file name) to translate, in one of these "
            + "formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm."
        ),
    )
    model: Union[Text, Literal["whisper-1"]] = Field(
        ...,
        description=(
            "ID of the model to use. Only `whisper-1` (which is powered by "
            + "our open source Whisper V2 model) is currently available."
        ),
    )
    prompt: Optional[Text] = Field(
        None,
        description=(
            "An optional text to guide the model's style or continue a previous audio "
            + "segment. The prompt should be in English."
        ),
    )
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = (
        Field(
            None,
            description=(
                "The format of the transcript output, in one of these options: "
                + "`json`, `text`, `srt`, `verbose_json`, or `vtt`."
            ),
        )
    )
    temperature: Optional[float] = Field(
        None,
        description=(
            "The sampling temperature, between 0 and 1. "
            + "Higher values like 0.8 will make the output more random, while "
            + "lower values like 0.2 will make it more focused and deterministic. "
            + "If set to 0, the model will use "
            + "[log probability](https://en.wikipedia.org/wiki/Log_probability) to "
            + "automatically increase the temperature until certain thresholds are hit."
        ),
    )
    timeout: Optional[float] = Field(
        None,
        description=(
            "Override the client-level default timeout for this request, in seconds."
        ),
    )

    def to_files_form(self) -> Dict[Text, Any]:
        out = {
            "file": self.file,
            "model": (None, self.model),
        }
        if self.prompt is not None:
            out["prompt"] = (None, self.prompt)
        if self.response_format is not None:
            out["response_format"] = (None, self.response_format)
        if self.temperature is not None:
            out["temperature"] = (None, self.temperature)
        if self.timeout is not None:
            out["timeout"] = (None, self.timeout)
        return out
