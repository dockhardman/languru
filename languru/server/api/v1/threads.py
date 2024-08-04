from concurrent.futures import ThreadPoolExecutor
from typing import List, Literal, Optional, Text, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import Path as QueryPath
from fastapi import Query, Request
from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.thread_deleted import ThreadDeleted
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.message_deleted import MessageDeleted
from openai.types.beta.threads.run import Run
from pyassorted.asyncio.executor import run_func

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.executor import depends_executor
from languru.server.deps.openai_backend import depends_openai_backend
from languru.server.deps.openai_threads import (
    depends_thread_id_run_messages_assistant_openai_client_backend,
)
from languru.tasks.openai_threads import task_openai_threads_runs_create
from languru.types.openai_page import OpenaiPage
from languru.types.openai_threads import (
    RunSubmitToolOutputsRequest,
    ThreadCreateAndRunRequest,
    ThreadCreateRequest,
    ThreadsMessageCreate,
    ThreadsMessageUpdate,
    ThreadsRunUpdate,
    ThreadUpdateRequest,
)
from languru.utils.openai_utils import rand_openai_id

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

    thread_id = rand_openai_id("thread")
    thread = await run_func(
        openai_backend.threads.create,
        thread=thread_create_request.to_openai_thread(thread_id),
        messages=[
            m.to_openai_message(thread_id=thread_id)
            for m in thread_create_request.messages or []
        ],
    )
    return thread


# https://platform.openai.com/docs/api-reference/threads/getThread
@router.get("/threads/{thread_id}")
async def get_thread(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to retrieve.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Thread:
    """Get a thread."""

    try:
        thread = await run_func(
            openai_backend.threads.retrieve,
            thread_id=thread_id,
        )
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return thread


# https://platform.openai.com/docs/api-reference/threads/modifyThread
@router.post("/threads/{thread_id}")
async def update_thread(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to update.",
    ),
    thread_update_request: ThreadUpdateRequest = Body(
        ...,
        description="The parameters for updating a thread.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Thread:
    """Update a thread."""

    thread = await run_func(
        openai_backend.threads.update,
        thread_id=thread_id,
        metadata=thread_update_request.metadata,
        tool_resources=thread_update_request.tool_resources,
    )
    return thread


# https://platform.openai.com/docs/api-reference/threads/deleteThread
@router.delete("/threads/{thread_id}")
async def delete_thread(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to delete.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> ThreadDeleted:
    """Delete a thread."""

    try:
        thread = await run_func(
            openai_backend.threads.delete,
            thread_id=thread_id,
        )
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return thread


# https://platform.openai.com/docs/api-reference/messages/createMessage
@router.post("/threads/{thread_id}/messages")
async def create_message(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to create a message in.",
    ),
    message_create_request: ThreadsMessageCreate = Body(
        ...,
        description="The parameters for creating a message.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Message:
    """Create a message in a thread."""

    message = await run_func(
        openai_backend.threads.messages.create,
        message=message_create_request.to_openai_message(thread_id=thread_id),
    )
    return message


# https://platform.openai.com/docs/api-reference/messages/listMessages
@router.get("/threads/{thread_id}/messages")
async def list_messages(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to list messages in.",
    ),
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
) -> OpenaiPage[Message]:
    """List all messages in a thread."""

    messages = await run_func(
        openai_backend.threads.messages.list,
        thread_id=thread_id,
        after=after,
        before=before,
        limit=limit,
        order=order,
    )
    return OpenaiPage(
        data=messages,
        object="list",
        first_id=messages[0].id if messages else None,
        last_id=messages[-1].id if messages else None,
    )


# https://platform.openai.com/docs/api-reference/messages/getMessage
@router.get("/threads/{thread_id}/messages/{message_id}")
async def get_message(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the message.",
    ),
    message_id: Text = QueryPath(
        ...,
        description="The ID of the message to retrieve.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Message:
    """Get a message in a thread."""

    try:
        message = await run_func(
            openai_backend.threads.messages.retrieve,
            thread_id=thread_id,
            message_id=message_id,
        )
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return message


# https://platform.openai.com/docs/api-reference/messages/modifyMessage
@router.post("/threads/{thread_id}/messages/{message_id}")
async def update_message(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the message.",
    ),
    message_id: Text = QueryPath(
        ...,
        description="The ID of the message to update.",
    ),
    message_update_request: ThreadsMessageUpdate = Body(
        ...,
        description="The parameters for updating a message.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Message:
    """Update a message in a thread."""

    message = await run_func(
        openai_backend.threads.messages.update,
        thread_id=thread_id,
        message_id=message_id,
        metadata=message_update_request.metadata,
    )
    return message


# https://platform.openai.com/docs/api-reference/messages/deleteMessage
@router.delete("/threads/{thread_id}/messages/{message_id}")
async def delete_message(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the message.",
    ),
    message_id: Text = QueryPath(
        ...,
        description="The ID of the message to delete.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> MessageDeleted:
    """Delete a message in a thread."""

    try:
        message_deleted = await run_func(
            openai_backend.threads.messages.delete,
            thread_id=thread_id,
            message_id=message_id,
        )
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return message_deleted


# https://platform.openai.com/docs/api-reference/runs/createRun
@router.post("/threads/{thread_id}/runs")
async def create_run(
    request: Request,
    delay: Optional[int] = Query(
        None, description="The delay in milliseconds before task execution."
    ),
    sleep: Optional[int] = Query(
        None, description="The sleep in milliseconds after chat completion."
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    thread_id_run_messages_assistant_openai_client_backend: Tuple[
        Text, Run, List[Message], Assistant, OpenAI, OpenaiBackend
    ] = Depends(depends_thread_id_run_messages_assistant_openai_client_backend),
    executor: ThreadPoolExecutor = Depends(depends_executor),
) -> Run:
    """Create a run in a thread."""

    (
        _,
        run,
        messages,
        _,
        openai_client,
        openai_backend,
    ) = thread_id_run_messages_assistant_openai_client_backend

    # Save the in-queue run
    run = await run_func(openai_backend.threads.runs.create, run=run)

    executor.submit(
        task_openai_threads_runs_create,
        run=run,
        messages=messages,
        openai_client=openai_client,
        openai_backend=openai_backend,
        delay=delay,
        sleep=sleep,
    )
    return run


# https://platform.openai.com/docs/api-reference/runs/createThreadAndRun
@router.post("/threads/runs")
async def create_thread_and_run(
    request: Request,
    thread_create_and_run_request: ThreadCreateAndRunRequest = Body(
        ...,
        description="The parameters for creating a thread and running an assistant.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Run:
    """Create a thread and run an assistant in it."""

    thread, messages = thread_create_and_run_request.to_openai_thread_and_messages()
    assistant = await run_func(
        openai_backend.assistants.retrieve,
        assistant_id=thread_create_and_run_request.assistant_id,
    )
    run = thread_create_and_run_request.to_openai_run(
        thread_id=thread.id, assistant_instructions=assistant.instructions
    )
    thread = await run_func(
        openai_backend.threads.create, thread=thread, messages=messages
    )
    run = await run_func(openai_backend.threads.runs.create, run=run)
    return run


# https://platform.openai.com/docs/api-reference/runs/listRuns
@router.get("/threads/{thread_id}/runs")
async def list_runs(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread to list runs in.",
    ),
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
    assistant_id: Optional[Text] = Query(
        None,
        description="The ID of the assistant to filter runs by.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> OpenaiPage[Run]:
    """List all runs in a thread."""

    runs = await run_func(
        openai_backend.threads.runs.list,
        thread_id=thread_id,
        after=after,
        before=before,
        limit=limit,
        order=order,
        assistant_id=assistant_id,
    )
    return OpenaiPage(
        data=runs,
        object="list",
        first_id=runs[0].id if runs else None,
        last_id=runs[-1].id if runs else None,
    )


# https://platform.openai.com/docs/api-reference/runs/getRun
@router.get("/threads/{thread_id}/runs/{run_id}")
async def get_run(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the run.",
    ),
    run_id: Text = QueryPath(
        ...,
        description="The ID of the run to retrieve.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Run:
    """Get a run in a thread."""

    try:
        run = await run_func(
            openai_backend.threads.runs.retrieve, run_id=run_id, thread_id=thread_id
        )
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return run


# https://platform.openai.com/docs/api-reference/runs/modifyRun
@router.post("/threads/{thread_id}/runs/{run_id}")
async def update_run(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the run.",
    ),
    run_id: Text = QueryPath(
        ...,
        description="The ID of the run to update.",
    ),
    run_update_request: ThreadsRunUpdate = Body(
        ...,
        description="The parameters for updating a run.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Run:
    """Update a run in a thread."""

    run = await run_func(
        openai_backend.threads.runs.update,
        run_id=run_id,
        thread_id=thread_id,
        cancelled_at=run_update_request.cancelled_at,
        completed_at=run_update_request.completed_at,
        expires_at=run_update_request.expires_at,
        failed_at=run_update_request.failed_at,
        incomplete_details=run_update_request.incomplete_details,
        instructions=run_update_request.instructions,
        last_error=run_update_request.last_error,
        max_completion_tokens=run_update_request.max_completion_tokens,
        max_prompt_tokens=run_update_request.max_prompt_tokens,
        metadata=run_update_request.metadata,
        model=run_update_request.model,
        parallel_tool_calls=run_update_request.parallel_tool_calls,
        required_action=run_update_request.required_action,
        response_format=run_update_request.response_format,
        started_at=run_update_request.started_at,
        status=run_update_request.status,
        tool_choice=run_update_request.tool_choice,
        tools=run_update_request.tools,
        truncation_strategy=run_update_request.truncation_strategy,
        usage=run_update_request.usage,
        temperature=run_update_request.temperature,
        top_p=run_update_request.top_p,
    )
    return run


# https://platform.openai.com/docs/api-reference/runs/submitToolOutputs
@router.post("/threads/{thread_id}/runs/{run_id}/submit_tool_outputs")
async def submit_tool_outputs(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the run.",
    ),
    run_id: Text = QueryPath(
        ...,
        description="The ID of the run to submit tool outputs for.",
    ),
    run_submit_tool_outputs_request: RunSubmitToolOutputsRequest = Body(
        ...,
        description="The parameters for submitting tool outputs for a run.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Run:
    """Submit tool outputs for a run in a thread."""

    raise HTTPException(status_code=501, detail="Not implemented")


# https://platform.openai.com/docs/api-reference/runs/cancelRun
@router.post("/threads/{thread_id}/runs/{run_id}/cancel")
async def cancel_run(
    request: Request,
    thread_id: Text = QueryPath(
        ...,
        description="The ID of the thread containing the run.",
    ),
    run_id: Text = QueryPath(
        ...,
        description="The ID of the run to cancel.",
    ),
    settings: ServerBaseSettings = Depends(app_settings),
    openai_backend: OpenaiBackend = Depends(depends_openai_backend),
) -> Run:
    """Cancel a run in a thread."""

    raise HTTPException(status_code=501, detail="Not implemented")
