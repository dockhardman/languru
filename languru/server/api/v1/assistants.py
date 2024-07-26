from typing import Literal, Optional, Text

from fastapi import APIRouter, Depends, Query, Request
from openai.types.beta.assistant import Assistant
from pyassorted.asyncio.executor import run_func

from languru.resources.sql.openai.backend import OpenaiBackend
from languru.server.config import ServerBaseSettings
from languru.server.deps.common import app_settings
from languru.server.deps.openai_backend import depends_openai_backend
from languru.types.openai_page import OpenaiPage

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
