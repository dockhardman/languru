from textwrap import dedent
from typing import List, Optional, Text, TypeVar, Type, Dict, Union

from openai import OpenAI
from pydantic import BaseModel, EmailStr, Field
from languru.prompts import PromptTemplate
from languru.prompts.repositories.data_model import prompt_date_model_from_openai
from pyassorted.string import extract_code_blocks
import pyjson5

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
        prompt_template = PromptTemplate(prompt_date_model_from_openai)
        # Generate response
        chat_res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_template.format()},
                {
                    "role": "user",
                    "content": (
                        f"[Model Schema]\n{model_schema}\n[END Model Schema]\n\n"
                        + f"{content}"
                    ),
                },
            ],
            model=model,
            temperature=0.0,
        )
        chat_answer = chat_res.choices[0].message.content
        if chat_answer is None:
            raise ValueError("Failed to generate a response from the OpenAI API.")
        # Parse response
        code_blocks = extract_code_blocks(chat_answer, language="json")
        if len(code_blocks) == 0:
            raise ValueError(
                f"Failed to extract a JSON code block from the response: {chat_answer}"
            )
        code_block = code_blocks[0]  # Only one code block is expected
        json_data: Union[Dict, List[Dict]] = pyjson5.loads(code_block)
        if isinstance(json_data, Dict):
            json_data = [json_data]
        return [cls.model_validate(item) for item in json_data]

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


class Tag(DataModel):
    name: Text
    description: Optional[Text] = None


class User(DataModel):
    name: Text
    username: Text
    email: EmailStr
    age: Optional[int] = None
    address: Optional[Text] = None
    tags: Optional[List[Tag]] = None


if __name__ == "__main__":
    OpenAI()
    User.model_from_openai(
        dedent(
            """
            User Information
            Name: John Doe
            Date of Birth: January 1, 1990
            Email: johndoe@example.com
            Phone: (555) 123-4567
            Address: 123 Main St, Anytown, USA 12345

            Account Details
            Username: johndoe90
            Account Number: 1234567890
            Account Type: Premium
            Subscription Start Date: May 1, 2023
            Subscription End Date: April 30, 2024

            Payment Information
            Payment Method: Visa Credit Card
            Card Number: **** **** **** 1234
            Expiration Date: 12/2025
            Billing Address: 123 Main St, Anytown, USA 12345

            Preferences
            Language: English
            Time Zone: Eastern Standard Time (EST)
            Email Notifications: Enabled
            SMS Notifications: Disabled
            Marketing Communications: Opted Out
            """
        ).strip(),
        OpenAI(),
    )
