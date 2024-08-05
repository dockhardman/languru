import time
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, cast

import pytz

from languru.config import console
from languru.utils.common import display_messages

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.beta.threads.message import Message as ThreadsMessage
    from openai.types.beta.threads.run import LastError, Run, Usage
    from openai.types.beta.threads.run_status import RunStatus
    from openai.types.chat.chat_completion import ChatCompletion

    from languru.resources.sql.openai.backend import OpenaiBackend


TERMINAL_RUN_STATUSES = ("cancelled", "failed", "completed", "incomplete", "expired")


def _update_run(
    run: "Run",
    openai_backend: "OpenaiBackend",
    *,
    status: Optional["RunStatus"] = None,
    cancelled_at: Optional[int] = None,
    started_at: Optional[int] = None,
    completed_at: Optional[int] = None,
    failed_at: Optional[int] = None,
    usage: Optional["Usage"] = None,
    last_error: Optional["LastError"] = None,
) -> "Run":
    """Update the task in-place."""

    run = openai_backend.threads.runs.update(
        run_id=run.id,
        thread_id=run.thread_id,
        status=status,
        cancelled_at=cancelled_at,
        started_at=started_at,
        completed_at=completed_at,
        failed_at=failed_at,
        usage=usage,
        last_error=last_error,
    )
    return run


def _update_run_if_cancelled(run: "Run", openai_backend: "OpenaiBackend") -> "Run":
    """Update the task if it is cancelled in-place.

    Parameters
    ----------
    run : Run
        The run object to update
    openai_backend : OpenaiBackend
        The OpenAI backend instance

    Returns
    -------
    bool
        True if the run is cancelled, False otherwise
    """

    if run.status == "cancelled":
        console.print(f"Run `{run.id}` is already cancelled. Cancelling the run.")
    elif run.status == "cancelling":
        run = _update_run(
            run, openai_backend, cancelled_at=int(time.time()), status="cancelled"
        )
        console.print(f"Run `{run.id}` is being cancelled.")
    return run


def _update_run_in_progress(run: "Run", openai_backend: "OpenaiBackend") -> "Run":
    """Update the task if it is in progress in-place."""

    run = _update_run(
        run, openai_backend, started_at=int(time.time()), status="in_progress"
    )
    return run


def _update_run_completed(
    run: "Run",
    openai_backend: "OpenaiBackend",
    *,
    chat_completion: Optional["ChatCompletion"] = None,
    with_creating_message: bool = True,
    threads_messages: Optional[List["ThreadsMessage"]] = None,
) -> "Run":
    """Update the task if it is completed in-place."""

    from openai.types.beta.threads.run import Usage

    from languru.types.openai_threads import to_openai_threads_message
    from languru.utils.openai_utils import ensure_openai_chat_completion_content

    if with_creating_message:
        if chat_completion is None:
            raise ValueError("chat_completion is required for creating a message")
        chat_answer = ensure_openai_chat_completion_content(chat_completion)
        completed_message = to_openai_threads_message(
            thread_id=run.thread_id,
            role="assistant",
            content=chat_answer,
        )
        if threads_messages is not None:
            threads_messages.append(completed_message)
        openai_backend.threads.messages.create(completed_message)

    run = _update_run(
        run,
        openai_backend,
        completed_at=int(time.time()),
        status="completed",
        usage=Usage.model_validate(
            (
                chat_completion.usage.model_dump(exclude_none=True)
                if chat_completion and chat_completion.usage
                else None
            ),
        ),
    )
    return run


def _update_run_failed(
    run: "Run", openai_backend: "OpenaiBackend", *, last_error: "LastError"
) -> "Run":
    """Update the task if it is failed in-place."""

    run = _update_run(
        run,
        openai_backend,
        status="failed",
        failed_at=int(time.time()),
        last_error=last_error,
    )
    return run


def task_openai_threads_runs_create(
    run: "Run",
    messages: List["ThreadsMessage"],
    *,
    openai_client: "OpenAI",
    openai_backend: "OpenaiBackend",
    delay: Optional[int] = None,
    sleep: Optional[int] = None,
    verbose: bool = True,
    **kwargs,
) -> "Run":
    """Create a new OpenAI Threads run and generate chat completions

    Parameters
    ----------
    run : Run
        The run object to create and generate completions for
    messages : List[ThreadsMessage]
        The list of messages in the thread
    openai_client : OpenAI
        The OpenAI client instance
    openai_backend : OpenaiBackend
        The OpenAI backend instance
    delay : Optional[int], optional
        The delay in milliseconds before starting the run, by default None
    sleep : Optional[int], optional
        The sleep in milliseconds after completing the run, by default None

    Returns
    -------
    Run
        The updated run object
    """

    from openai.types.beta.threads.run import LastError
    from openai.types.chat.chat_completion import ChatCompletion

    from languru.types.chat.completions import ChatCompletionRequest

    time_start = datetime.now(pytz.utc)
    console.print(
        f"[{time_start.isoformat(timespec='seconds')}] "
        + "Received `task_openai_threads_runs_create`."
    )

    if delay:
        console.print(f"Run '{run.id}' delaying for {delay} milliseconds...")
        time.sleep(delay / 1000)

    # Refresh the run from the backend
    run = openai_backend.threads.runs.retrieve(run_id=run.id, thread_id=run.thread_id)
    console.print(f"[{time_start.isoformat(timespec='seconds')}] Executing run: {run}")

    # Cancel the run if it is already cancelled
    run = _update_run_if_cancelled(run, openai_backend)

    # Return if the run is already in a terminal state
    if run.status in TERMINAL_RUN_STATUSES:
        console.print(f"Run '{run.id}' is already in a terminal state: '{run.status}'")
        return run  # RETURN: run

    # Initialize the run
    run = _update_run_in_progress(run, openai_backend)

    # Prepare the chat completion request
    chat_completion_request = ChatCompletionRequest.from_openai_threads_run(
        run=run, messages=messages, stream=False  # Ensure synchronous completion
    )
    if verbose:
        display_messages(
            chat_completion_request.messages,
            table_title=f"Run '{run.id}' Input Messages",
        )
        console.print(f"Chat completion request: {chat_completion_request}")

    # Generate chat completions
    try:
        chat_completion_res = openai_client.chat.completions.create(
            **chat_completion_request.model_dump(exclude_none=True)
        )
        chat_completion_res = cast(ChatCompletion, chat_completion_res)

        # Update the run with the chat completion
        run = _update_run_completed(
            run,
            openai_backend,
            chat_completion=chat_completion_res,
            with_creating_message=True,
            threads_messages=messages,
        )
        if verbose:
            display_messages(
                messages[-1:], table_title=f"Run '{run.id}' Output Messages"
            )

    except Exception as e:
        console.print_exception()
        console.print(f"Error generating chat completions: {e}")
        run = _update_run_failed(
            run,
            openai_backend,
            last_error=LastError.model_validate(
                {"code": "server_error", "message": str(e)}
            ),
        )

    if sleep:
        console.print(f"Run '{run.id}' sleeping for {sleep} milliseconds...")
        time.sleep(sleep / 1000)

    # Finish the run
    console.print(f"Run '{run.id}' completed: {run}")
    return run
