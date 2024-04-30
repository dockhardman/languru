from typing import Any, Dict, Literal, Optional, Text, Union

from openai._types import FileTypes
from pydantic import BaseModel, ConfigDict, Field


class ImagesGenerationsRequest(BaseModel):
    prompt: Text = Field(
        ...,
        description="A text description of the desired image(s). The maximum length is 1000 characters for `dall-e-2` and 4000 characters for `dall-e-3`.",  # noqa: E501
    )
    model: Union[Text, Literal["dall-e-2", "dall-e-3"]] = Field(
        ..., description="The model to use for image generation."
    )
    n: Optional[int] = Field(
        None,
        description="The number of images to generate. Must be between 1 and 10. For `dall-e-3`, only `n=1` is supported.",  # noqa: E501
    )
    quality: Optional[Literal["standard", "hd"]] = Field(
        None,
        description="The quality of the image that will be generated. `hd` creates images with finer details and greater consistency across the image. This param is only supported for `dall-e-3`.",  # noqa: E501
    )
    response_format: Optional[Literal["url", "b64_json"]] = Field(
        None,
        description="The format in which the generated images are returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes after the image has been generated.",  # noqa: E501
    )
    size: Optional[
        Union[
            Text, Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
        ]
    ] = Field(
        None,
        description="The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`. Must be one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3` models.",  # noqa: E501
    )
    style: Optional[Literal["vivid", "natural"]] = Field(
        None,
        description="The style of the generated images. Must be one of `vivid` or `natural`. Vivid causes the model to lean towards generating hyper-real and dramatic images. Natural causes the model to produce more natural, less hyper-real looking images. This param is only supported for `dall-e-3`.",  # noqa: E501
    )
    user: Optional[Text] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).",  # noqa: E501
    )
    timeout: Optional[float] = Field(
        None,
        description="Override the client-level default timeout for this request, in seconds.",  # noqa: E501
    )


class ImagesEditRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image: FileTypes = Field(
        ...,
        description="The image to edit. Must be a valid PNG file, less than 4MB, and square. If mask is not provided, image must have transparency, which will be used as the mask.",  # noqa: E501
    )
    prompt: Text = Field(
        ...,
        description="A text description of the desired image(s). The maximum length is 1000 characters.",  # noqa: E501
    )
    mask: Optional[FileTypes] = Field(
        None,
        description="An additional image whose fully transparent areas (e.g. where alpha is zero) indicate where `image` should be edited. Must be a valid PNG file, less than 4MB, and have the same dimensions as `image`.",  # noqa: E501
    )
    model: Optional[Union[Text, Literal["dall-e-2"]]] = Field(
        None,
        description="The model to use for image generation. Only `dall-e-2` is supported at this time.",  # noqa: E501
    )
    n: Optional[int] = Field(
        None,
        description="The number of images to generate. Must be between 1 and 10.",  # noqa: E501
    )
    response_format: Optional[Literal["url", "b64_json"]] = Field(
        None,
        description="The format in which the generated images are returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes after the image has been generated.",  # noqa: E501
    )
    size: Optional[Union[Text, Literal["256x256", "512x512", "1024x1024"]]] = Field(
        None,
        description="The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.",  # noqa: E501
    )
    user: Optional[Text] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).",  # noqa: E501
    )
    timeout: Optional[float] = Field(
        None,
        description="Override the client-level default timeout for this request, in seconds.",  # noqa: E501
    )

    def to_files_form(self) -> Dict[Text, Any]:
        out = {
            "image": self.image,
            "prompt": (None, self.prompt),
        }
        if self.mask is not None:
            out["mask"] = self.mask
        if self.model is not None:
            out["model"] = (None, self.model)
        if self.n is not None:
            out["n"] = (None, self.n)
        if self.response_format is not None:
            out["response_format"] = (None, self.response_format)
        if self.size is not None:
            out["size"] = (None, self.size)
        if self.user is not None:
            out["user"] = (None, self.user)
        if self.timeout is not None:
            out["timeout"] = (None, self.timeout)
        return out


class ImagesVariationsRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image: FileTypes = Field(
        ...,
        description="The image to use as the basis for the variation(s). Must be a valid PNG file, less than 4MB, and square.",  # noqa: E501
    )
    model: Optional[Union[Text, Literal["dall-e-2"]]] = Field(
        None,
        description="The model to use for image generation. Only `dall-e-2` is supported at this time.",  # noqa: E501
    )
    n: Optional[int] = Field(
        None,
        description="The number of images to generate. Must be between 1 and 10. For `dall-e-3`, only `n=1` is supported.",  # noqa: E501
    )
    response_format: Optional[Literal["url", "b64_json"]] = Field(
        None,
        description="The format in which the generated images are returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes after the image has been generated.",  # noqa: E501
    )
    size: Optional[Union[Text, Literal["256x256", "512x512", "1024x1024"]]] = Field(
        None,
        description="The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.",  # noqa: E501
    )
    user: Optional[Text] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).",  # noqa: E501
    )
    timeout: Optional[float] = Field(
        None,
        description="Override the client-level default timeout for this request, in seconds.",  # noqa: E501
    )

    def to_files_form(self) -> Dict[Text, Any]:
        out: Dict[Text, Any] = {
            "image": self.image,
        }
        if self.model is not None:
            out["model"] = (None, self.model)
        if self.n is not None:
            out["n"] = (None, self.n)
        if self.response_format is not None:
            out["response_format"] = (None, self.response_format)
        if self.size is not None:
            out["size"] = (None, self.size)
        if self.user is not None:
            out["user"] = (None, self.user)
        if self.timeout is not None:
            out["timeout"] = (None, self.timeout)
        return out
