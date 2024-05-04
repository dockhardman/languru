from textwrap import dedent
from typing import List, Optional, Text

from openai import OpenAI
from pydantic import BaseModel, EmailStr
from rich import print


class DataModel(BaseModel):
    @classmethod
    def model_from_openai(
        cls, content: Text, client: "OpenAI", model: Text = "gpt-3.5-turbo", **kwargs
    ):
        schema = cls.model_json_schema()
        model_schema = {cls.__name__: schema}
        sys_prompt = dedent(
            """
            ## Objective
            The assistant is tasked with parsing and understanding user inputs based on predefined criteria specified in an OpenAPI format. The assistant will extract key information from the user's statements and generate a detailed response.

            ## Input Parsing
            The assistant should meticulously analyze the user's input to identify and extract the relevant data points specified in the following OpenAPI schema excerpt:

            ```json
            # Example OpenAPI schema of the data model
            {"UserData": {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "interests": {"type": "array", "items": {"type": "string"}}}, "required": ["name", "age"]}}
            ```

            ## Response Format
            Upon processing the input, the assistant must provide a clear explanation of the user's statement, outlining the identified and extracted data points. The response should culminate in a JSON-formatted block that encapsulates the analysis results, adhering strictly to the format outlined below:

            1. Begin with a brief explanation of the user's input based on the extracted information.
            2. Present the final result encapsulated in a JSON block.

            ## Example Response

            ```plaintext
            Based on your input, the assistant has identified the following details: Name, Age, and Interests. Here is the structured representation of the information extracted:

            ```json
            {"name": "John Doe", "age": 30, "interests": ["reading", "gaming", "hiking"]}
            ```
            ```

            ## Instructions
            The assistant should ensure accuracy in data extraction and maintain a formal and respectful tone throughout the interaction. The JSON block should start with "```json" and end with "```" to clearly demarcate the structured data output.
            """
        ).strip()
        chat_res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": f"[Model Schema]\n{model_schema}\n[END Model Schema]\n\n{content}",
                },
            ],
            model=model,
            temperature=0.0,
        )
        print(chat_res.choices[0].message.content)


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
