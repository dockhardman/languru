from logging import Logger
from typing import Optional, Tuple

from fastapi import Body, Depends, Request
from openai import OpenAI

from languru.config import logger as languru_logger
from languru.examples.openapi.chat import chat_openapi_examples
from languru.server.deps.openai_clients import openai_client_from_model, openai_clients
from languru.server.utils.common import get_value_from_app, to_openapi_examples
from languru.types.chat.completions import ChatCompletionRequest
from languru.types.organizations import OrganizationType
from languru.utils.common import display_object


def depends_openai_client_chat_completion_request(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    chat_completion_request: ChatCompletionRequest = Body(
        ...,
        openapi_examples=to_openapi_examples(chat_openapi_examples),
    ),
) -> Tuple[OpenAI, ChatCompletionRequest]:
    """Returns the OpenAI client and the chat completion request."""

    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    openai_client, org_type, chat_completion_request.model = openai_client_from_model(
        chat_completion_request.model, org_type=org_type
    )

    logger.debug(
        "Depends OpenAI client chat completion request: "
        + f"organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{chat_completion_request.model}'"
    )
    return (openai_client, chat_completion_request)
