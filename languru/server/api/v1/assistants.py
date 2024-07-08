from typing import Literal, Optional, Text

from fastapi import APIRouter, Depends, Query, Request
from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant
from pyassorted.asyncio.executor import run_func

from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_clients import openai_clients

router = APIRouter()


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
    limit: Optional[int] = Query(
        None,
        description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.",  # noqa: E501
    ),
    order: Optional[Literal["asc", "desc"]] = Query(
        None,
        description="Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.",  # noqa: E501
    ),
    settings: ServerBaseSettings = Depends(app_settings),
) -> SyncCursorPage[Assistant]:
    params = {}
    if after is not None:
        params["after"] = after
    if before is not None:
        params["before"] = before
    if limit is not None:
        params["limit"] = limit
    if order is not None:
        params["order"] = order
    if openai_clients._oai_client is None:
        return SyncCursorPage.model_validate({"data": []})
    return await run_func(openai_clients._oai_client.beta.assistants.list, **params)
