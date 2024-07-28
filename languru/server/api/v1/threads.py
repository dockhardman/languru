from typing import Literal, Optional, Text

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import Path as QueryPath
from fastapi import Query, Request
from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.thread import Thread
from pyassorted.asyncio.executor import run_func

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_backend import depends_openai_backend
from languru.types.openai_assistant_create import AssistantCreateRequest
from languru.types.openai_assistant_update import AssistantUpdateRequest
from languru.types.openai_page import OpenaiPage
from languru.types.openai_threads import ThreadCreateRequest

router = APIRouter()


@router.get("/threads")
async def list_threads(
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
) -> OpenaiPage[Thread]:
    """List all threads."""

    threads = await run_func(
        openai_backend.threads.list,
        after=after,
        before=before,
        limit=limit,
        order=order,
    )
    return OpenaiPage(
        data=threads,
        object="list",
        first_id=threads[0].id if threads else None,
        last_id=threads[-1].id if threads else None,
    )


# https://platform.openai.com/docs/api-reference/threads/createThread
@router.post("/threads")
async def create_thread(
    request: Request,
    thread_create_request: ThreadCreateRequest = Body(
        ...,
        description="The parameters for creating a thread.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Thread:
    """Create a thread."""

    thread = await run_func(
        openai_backend.threads.create,
        thread=thread_create_request.to_openai_thread(),
        messages=[m.to_openai_message() for m in thread_create_request.messages or []],
    )
    return thread


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
