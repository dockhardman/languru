import time
from datetime import datetime
from typing import TYPE_CHECKING, List, cast

import pytz

from languru.config import console
from languru.utils.common import display_messages

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.beta.threads.message import Message as ThreadsMessage
    from openai.types.beta.threads.run import Run

    from languru.resources.sql.openai.backend import OpenaiBackend


def task_openai_threads_runs_create(
    run: "Run",
    messages: List["ThreadsMessage"],
    *,
    openai_client: "OpenAI",
    openai_backend: "OpenaiBackend",
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

    Returns
    -------
    Run
        The updated run object
    """

    from openai.types.beta.threads.run import LastError, Usage
    from openai.types.chat.chat_completion import ChatCompletion

    from languru.types.chat.completions import ChatCompletionRequest, Message
    from languru.types.openai_threads import to_openai_threads_message
    from languru.utils.openai_utils import ensure_openai_chat_completion_content

    time_start = datetime.now(pytz.utc)
    console.print(
        f"[{time_start.isoformat(timespec='seconds')}] "
        + f"Starting `task_openai_threads_runs_create` with run: {run}"
    )

    # Cancel the run if it is already cancelled
    if run.status == "cancelled":
        console.print(f"Run `{run.id}` is already cancelled. Cancelling the run.")
        return run  # RETURN: run
    elif run.status == "cancelling":
        run.cancelled_at = int(time.time())
        run.status = "cancelled"
        openai_backend.threads.runs.update(
            run_id=run.id,
            thread_id=run.thread_id,
            cancelled_at=run.cancelled_at,
            status=run.status,
        )
        console.print(f"Run `{run.id}` is being cancelled.")
        return run  # RETURN: run

    # Initialize the run
    run.started_at = int(time.time())
    run.status = "in_progress"
    openai_backend.threads.runs.update(
        run_id=run.id,
        thread_id=run.thread_id,
        started_at=run.started_at,
        status=run.status,
    )

    # Prepare the chat completion request
    chat_messages: List["Message"] = []
    if run.instructions:
        chat_messages.append(
            Message.model_validate({"role": "system", "content": run.instructions})
        )
    for m in messages:
        chat_messages.append(Message.from_openai_threads_message(m))
    chat_completion_request = ChatCompletionRequest.model_validate(
        {"messages": chat_messages, "model": run.model, "temperature": run.temperature}
    )
    chat_completion_request.stream = False  # Ensure synchronous completion
    if verbose:
        display_messages(chat_messages, table_title=f"Run '{run.id}' Input Messages")
        console.print(f"Chat completion request: {chat_completion_request}")

    # Generate chat completions
    try:
        chat_completion_res = openai_client.chat.completions.create(
            **chat_completion_request.model_dump(exclude_none=True)
        )
        chat_completion_res = cast(ChatCompletion, chat_completion_res)
        chat_answer = ensure_openai_chat_completion_content(chat_completion_res)
        if verbose:
            display_messages(
                [{"role": "assistant", "content": chat_answer}],
                table_title=f"Run '{run.id}' Output Messages",
            )
        run.completed_at = int(time.time())
        run.status = "completed"
        if chat_completion_res.usage:
            run.usage = Usage.model_validate(
                chat_completion_res.usage.model_dump(exclude_none=True)
            )
        openai_backend.threads.messages.create(
            to_openai_threads_message(
                thread_id=run.thread_id,
                role="assistant",
                content=chat_answer,
            )
        )
    except Exception as e:
        console.print_exception()
        console.print(f"Error generating chat completions: {e}")
        run.failed_at = int(time.time())
        run.last_error = LastError.model_validate(
            {"code": "server_error", "message": str(e)}
        )
        run.status = "failed"

    # Finish the run
    console.print(f"Run '{run.id}' completed: {run}")
    openai_backend.threads.runs.update(
        run_id=run.id,
        thread_id=run.thread_id,
        failed_at=run.failed_at,
        completed_at=run.completed_at,
        status=run.status,
        usage=run.usage,
        last_error=run.last_error,
    )
    return run
