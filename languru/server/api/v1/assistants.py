from typing import Literal, Optional, Text

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import Path as QueryPath
from fastapi import Query, Request
from openai.types.beta.assistant import Assistant
from pyassorted.asyncio.executor import run_func

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_backend import depends_openai_backend
from languru.types.openai_assistant_create import AssistantCreateRequest
from languru.types.openai_page import OpenaiPage

router = APIRouter()


# https://platform.openai.com/docs/api-reference/assistants/listAssistants
@router.get("/assistants")
async def list_assistants(
    request: Request,
    after: Optional[Text] = Query(
        None,
        description="`after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.",  # noqa: E501
    ),
    before: Optional[Text] = Query(
        None,
        description="`before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.",  # noqa: E501
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.",  # noqa: E501
    ),
    order: Optional[Literal["asc", "desc"]] = Query(
        None,
        description="Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.",  # noqa: E501
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> OpenaiPage[Assistant]:
    """List all assistants."""

    assistants = await run_func(
        openai_backend.assistants.list,
        after=after,
        before=before,
        limit=limit,
        order=order,
    )
    return OpenaiPage(
        data=assistants,
        object="list",
        first_id=assistants[0].id if assistants else None,
        last_id=assistants[-1].id if assistants else None,
        has_more=len(assistants) >= limit,
    )


# https://platform.openai.com/docs/api-reference/assistants/createAssistant
@router.post("/assistants")
async def create_assistant(
    request: Request,
    assistant_create_request: AssistantCreateRequest = Body(
        ...,
        description="The request to create an assistant.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Assistant:
    """Create an assistant."""

    try:
        assistant = await run_func(
            openai_backend.assistants.create,
            assistant_create_request.to_assistant(),
        )
        return assistant
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# https://platform.openai.com/docs/api-reference/assistants/getAssistant
@router.get("/assistants/{assistant_id}")
async def get_assistant(
    request: Request,
    assistant_id: Text = QueryPath(..., description="The ID of the assistant."),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Assistant:
    """Retrieve an assistant by ID."""

    try:
        assistant = await run_func(openai_backend.assistants.retrieve, assistant_id)
        return assistant
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# https://platform.openai.com/docs/api-reference/assistants/modifyAssistant
# @router.post("/assistants/{assistant_id}")


# https://platform.openai.com/docs/api-reference/assistants/deleteAssistant
# @router.delete("/assistants/{assistant_id}")


# https://platform.openai.com/docs/api-reference/threads/createThread
# @router.post("/threads")


# https://platform.openai.com/docs/api-reference/threads/getThread
# @router.get("/threads/{thread_id}")


# https://platform.openai.com/docs/api-reference/threads/modifyThread
# @router.post("/threads/{thread_id}")


# https://platform.openai.com/docs/api-reference/threads/deleteThread
# @router.delete("/threads/{thread_id}")


# https://platform.openai.com/docs/api-reference/messages/createMessage
# @router.post("/threads/{thread_id}/messages")


# https://platform.openai.com/docs/api-reference/messages/listMessages
# @router.get("/threads/{thread_id}/messages")


# https://platform.openai.com/docs/api-reference/messages/getMessage
# @router.get("/threads/{thread_id}/messages/{message_id}")


# https://platform.openai.com/docs/api-reference/messages/modifyMessage
# @router.post("/threads/{thread_id}/messages/{message_id}")


# https://platform.openai.com/docs/api-reference/messages/deleteMessage
# @router.delete("/threads/{thread_id}/messages/{message_id}")


# https://platform.openai.com/docs/api-reference/runs/createRun
# @router.post("/threads/{thread_id}/runs")


# https://platform.openai.com/docs/api-reference/runs/createThreadAndRun
# @router.post("/threads/runs")


# https://platform.openai.com/docs/api-reference/runs/listRuns
# @router.get("/threads/{thread_id}/runs")


# https://platform.openai.com/docs/api-reference/runs/getRun
# @router.get("/threads/{thread_id}/runs/{run_id}")


# https://platform.openai.com/docs/api-reference/runs/modifyRun
# @router.post("/threads/{thread_id}/runs/{run_id}")


# https://platform.openai.com/docs/api-reference/runs/submitToolOutputs
# @router.post("/threads/{thread_id}/runs/{run_id}/submit_tool_outputs")


# https://platform.openai.com/docs/api-reference/runs/cancelRun
# @router.post("/threads/{thread_id}/runs/{run_id}/cancel")
