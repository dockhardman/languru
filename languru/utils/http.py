import json
import logging
from typing import Any, Dict, Generator, Iterable, List, Literal, Optional, Text, Union

import httpx
from pydantic import BaseModel

from languru.config import logger as languru_logger


async def requests_stream_lines(
    url: Text,
    data: Optional[Dict[Text, Any]] = None,
    method: Literal["POST", "GET"] = "POST",
    headers: Optional[Dict[Text, Text]] = None,
):
    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream(
            method, str(url), json=data, headers=headers or None
        ) as response:
            async for chunk in response.aiter_lines():
                yield chunk + "\n"


def simple_sse_encode(
    stream: Union[
        Iterable[Union[Text, Dict, List[Any], BaseModel]],
        Generator[Union[Text, Dict, List[Any], BaseModel], None, None],
    ],
    logger: Optional[Union[Text, "logging.Logger"]] = None,
) -> Generator[Text, None, None]:
    logger = logger or languru_logger
    logger = logging.getLogger(logger) if isinstance(logger, Text) else logger
    has_warned = False
    for item in stream:
        if isinstance(item, BaseModel):
            yield f"data: {item.model_dump_json()}\n\n"
        elif isinstance(item, (Dict, List)):
            yield f"data: {json.dumps(item)}\n\n"
        elif isinstance(item, Text):
            yield f"data: {item}\n\n"
        else:
            if has_warned is False:
                logger.warning(
                    f"Unknown type {type(item)} in stream, using str() to encode."
                )
                has_warned = True
            yield f"data: {str(item)}\n\n"
    yield "data: [DONE]\n\n"
