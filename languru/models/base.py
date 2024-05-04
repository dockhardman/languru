from typing import Dict, List, Text, Type, TypeVar

import pyjson5
from openai import OpenAI
from pyassorted.string import extract_code_blocks
from pydantic import BaseModel
from pydantic_core import ValidationError

from languru.prompts import PromptTemplate
from languru.prompts.repositories.data_model import prompt_date_model_from_openai
from languru.utils.common import ensure_list, ensure_openai_chat_completion_content

DataModelTypeVar = TypeVar("DataModelTypeVar", bound="DataModel")


class DataModel(BaseModel):
    @classmethod
    def models_from_openai(
        cls: Type[DataModelTypeVar],
        content: Text,
        client: "OpenAI",
        model: Text = "gpt-3.5-turbo",
        **kwargs,
    ) -> List[DataModelTypeVar]:
        # Get schema
        schema = cls.model_json_schema()
        model_schema = {cls.__name__: schema}
        # Prepare prompt
        user_message = {
            "role": "user",
            "content": (
                "[Model Schema]\n{model_schema}\n[END Model Schema]\n\n{user_says}"
            ),
        }
        prompt_template = PromptTemplate(
            prompt_date_model_from_openai, messages=[user_message]
        )
        # Generate response
        chat_res = client.chat.completions.create(
            messages=prompt_template.format_messages(
                prompt_vars={"model_schema": model_schema, "user_says": content}
            ),
            model=model,
            temperature=0.0,
        )
        chat_answer = ensure_openai_chat_completion_content(chat_res)
        # Parse response
        code_blocks = extract_code_blocks(chat_answer, language="json")
        if len(code_blocks) == 0:
            raise ValueError(
                f"Failed to extract a JSON code block from the response: {chat_answer}"
            )
        code_block = code_blocks[0]  # Only one code block is expected
        items: List[Dict] = ensure_list(pyjson5.loads(code_block))
        # Validate models
        models: List[DataModelTypeVar] = []
        for item in items:
            try:
                _model = cls.model_validate(item)
            except ValidationError as e:
                raise ValueError(
                    f"Failed to validate model '{cls.__name__}' from data: {item}"
                ) from e
            models.append(_model)
        return models

    @classmethod
    def model_from_openai(
        cls: Type[DataModelTypeVar],
        content: Text,
        client: "OpenAI",
        model: Text = "gpt-3.5-turbo",
        **kwargs,
    ) -> DataModelTypeVar:
        models = cls.models_from_openai(content, client, model, **kwargs)  #
        if len(models) == 0:
            raise ValueError("Could not extract information from content.")
        return models[0]  # Only one model is expected
