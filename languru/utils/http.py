from typing import Any, Dict, Literal, Optional, Text

import httpx


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
