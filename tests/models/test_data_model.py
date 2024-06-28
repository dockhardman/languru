from textwrap import dedent
from typing import List, Optional, Text

import pytest
from openai import OpenAI
from pydantic import EmailStr, Field

from languru.models import DataModel


class Tag(DataModel):
    name: Text = Field(
        ..., description="The user characteristic information name of the tag."
    )
    description: Optional[Text] = Field(
        None, description="The description of the user characteristic information."
    )


class User(DataModel):
    name: Text = Field(..., description="The name of the user.")
    username: Optional[Text] = Field(
        None,
        description=(
            "The username of the user. If there is no username, "
            + "this field is set as the name."
        ),
    )
    email: Optional[EmailStr] = Field(
        ...,
        description=(
            "The email address of the user. If the user has not provided an "
            + "email address, this field is set to None."
        ),
    )
    age: Optional[int] = Field(None, description="The age of the user.")
    address: Optional[Text] = Field(
        None,
        description=(
            "The address of the user. This field contains the street address, "
            + "city, state, and postal code."
        ),
    )
    tags: Optional[List[Tag]] = Field(
        None,
        description=(
            "A list of tags associated with the user. Each tag contains a name "
            + "and an optional description."
        ),
    )


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            dedent(
                """
            In a recent study on the impact of social media on mental health, researchers interviewed two participants who shared their experiences. The first participant, Sarah Johnson (sarahjohnson@gmail.com), a 28-year-old marketing professional, reported feeling increased anxiety and stress due to the constant pressure to present a perfect life on her social media profiles. She stated, "I found myself constantly comparing my life to the highlight reels of others, and it made me feel like I was falling behind."
            The second participant, Michael Thompson (michaelthompson@yahoo.com), a 35-year-old teacher, discussed how social media affected his ability to concentrate and connect with others in real life. He mentioned, "I realized I was spending hours scrolling through my feeds, and it was taking away from quality time with my family and friends. I decided to limit my social media use and focus on building more meaningful relationships offline."
            These experiences highlight the importance of understanding the potential negative effects of social media on mental well-being and the need for individuals to develop healthy habits when engaging with these platforms.
            """  # noqa: E501
            ).strip(),
            True,
        ),
    ],
)
def test_models_from_openai(content, expected):
    res = User.model_from_openai(content, OpenAI())
    assert isinstance(res, List) and len(res) > 0
    assert expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (
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
                """  # noqa: E501
            ).strip(),
            True,
        ),
    ],
)
def test_model_from_openai(content, expected):
    res = User.model_from_openai(content, OpenAI())
    assert len(res) > 0
    assert all([isinstance(i, User) for i in res])
