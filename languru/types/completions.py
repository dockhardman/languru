from typing import Dict, List, Optional, Text, Union

from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    model: str
    prompt: Union[Text, List[Union[Text, List[int]]]]
    best_of: Optional[int] = Field(
        default=1,
        description="Generates best_of completions server-side and returns the 'best' one.",
    )
    echo: Optional[bool] = Field(
        default=False, description="Echo back the prompt in addition to the completion."
    )
    frequency_penalty: Optional[float] = Field(
        default=0,
        ge=-2.0,
        le=2.0,
        description="Penalize new tokens based on their frequency.",
    )
    logit_bias: Optional[Dict[int, int]] = Field(
        default=None,
        description="Modify the likelihood of specified tokens appearing in the completion.",
    )
    logprobs: Optional[int] = Field(
        default=None,
        ge=0,
        le=5,
        description="Include the log probabilities on the most likely output tokens.",
    )
    max_tokens: Optional[int] = Field(
        default=16,
        description="The maximum number of tokens that can be generated in the completion.",
    )
    n: Optional[int] = Field(
        default=1, description="How many completions to generate for each prompt."
    )
    presence_penalty: Optional[float] = Field(
        default=0,
        ge=-2.0,
        le=2.0,
        description="Penalize new tokens based on their presence.",
    )
    seed: Optional[int] = Field(
        default=None, description="If specified, sample deterministically."
    )
    stop: Optional[Union[Text, List[Text]]] = Field(
        default=None,
        description="Sequences where the API will stop generating further tokens.",
    )
    stream: Optional[bool] = Field(
        default=False, description="Whether to stream back partial progress."
    )
    suffix: Optional[Text] = Field(
        default=None,
        description="The suffix that comes after a completion of inserted text.",
    )
    temperature: Optional[float] = Field(
        default=1, ge=0, le=2, description="Sampling temperature to use."
    )
    top_p: Optional[float] = Field(
        default=1,
        ge=0,
        le=1,
        description="An alternative to sampling with temperature, called nucleus sampling.",
    )
    user: Optional[Text] = Field(
        default=None, description="A unique identifier representing your end-user."
    )
