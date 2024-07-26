from typing import Literal, Optional, Text

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi import Path as QueryPath
from fastapi import Query, Request
from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from pyassorted.asyncio.executor import run_func

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_backend import depends_openai_backend
from languru.types.openai_assistant_create import AssistantCreateRequest
from languru.types.openai_assistant_update import AssistantUpdateRequest
from languru.types.openai_page import OpenaiPage

router = APIRouter()


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
