from openai.types import Model as OpenaiModel
from pydantic import ConfigDict


class Model(OpenaiModel):
    model_config = ConfigDict(from_attributes=True)
