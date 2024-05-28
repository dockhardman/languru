import os
from typing import Optional, Text

import google.generativeai as genai
from openai import OpenAI

from languru.config import logger


class GoogleOpenAI(OpenAI):
    def __init__(self, *args, api_key: Optional[Text] = None, **kwargs):
        api_key = (
            api_key
            or os.getenv("GOOGLE_GENAI_API_KEY")
            or os.getenv("GOOGLE_AI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not api_key:
            logger.error("Google GenAI API key is not provided")
        genai.configure(api_key=api_key)
