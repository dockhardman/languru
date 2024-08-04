from logging import Logger
from typing import Optional, Text, Tuple

from fastapi import Body, Depends
from fastapi import Path as QueryPath
from fastapi import Request
from fastapi.exceptions import HTTPException
from openai import OpenAI
from openai.types.beta.threads.run import Run as ThreadsRun
from pyassorted.asyncio.executor import run_func

from languru.config import logger as languru_logger
from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.deps.openai_backend import depends_openai_backend
from languru.server.deps.openai_clients import openai_client_from_model, openai_clients
from languru.server.utils.common import get_value_from_app
from languru.types.openai_threads import ThreadsRunCreate
from languru.types.organizations import OrganizationType
from languru.utils.common import display_object


async def depends_thread_id_run_openai_client_backend(
    request: "Request",
    org_type: Optional[OrganizationType] = Depends(openai_clients.depends_org_type),
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to create a run in.",
    ),
    run_create_request: ThreadsRunCreate = Body(
        ...,
        description="The parameters for creating a run.",
    ),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Tuple[Text, ThreadsRun, OpenAI, OpenaiBackend]:
    """Returns the thread ID, the OpenAI threads run, the OpenAI client, and the backend."""  # noqa: E501

    logger = get_value_from_app(
        request.app, key="logger", value_typing=Logger, default=languru_logger
    )

    # Retrieve the model if not specified
    if run_create_request.model is None:
        logger.debug(
            "No model specified. Using assistant "
            + f"'{run_create_request.assistant_id}' model."
        )
        try:
            assistant_retrieved = await run_func(
                openai_backend.assistants.retrieve,
                assistant_id=run_create_request.assistant_id,
            )
            run_create_request.model = assistant_retrieved.model
        except NotFound:
            raise HTTPException(status_code=404, detail="Assistant not found.")

    # Retrieve the OpenAI client and the model name without organization type
    openai_client, org_type, run_create_request.model = openai_client_from_model(
        run_create_request.model, org_type=org_type
    )

    # Create the OpenAI threads run
    run = run_create_request.to_openai_run(thread_id=thread_id, status="queued")

    logger.debug(
        "Depends OpenAI client threads run create request: "
        + f"organization type: '{org_type}', "
        + f"openAI client: '{display_object(openai_client)}', "
        + f"model: '{run_create_request.model}'"
    )
    return (thread_id, run, openai_client, openai_backend)
