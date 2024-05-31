import json
from typing import Dict, List, Text, Union

from pydantic import BaseModel

from languru.config import logger


def simple_encode_sse(
    data: Union[bytes, Text, BaseModel, Dict, List],
    *,
    encoding: Text = "utf-8",
) -> bytes:
    """Simple encoding for Server-Sent Events (SSE).

    Parameters
    ----------
    data : Union[bytes, Text, BaseModel, Dict, List]
        The data to encode.
    encoding : str, optional
        The encoding to use. Defaults to 'utf-8'.

    Returns
    -------
    bytes
        The encoded data.
    """

    if isinstance(data, bytes):
        encoded_data = data
    elif isinstance(data, Text):
        encoded_data = data.encode(encoding)
    elif isinstance(data, BaseModel):
        encoded_data = json.dumps(data.model_dump(), default=str).encode(encoding)
    elif isinstance(data, Dict):
        encoded_data = json.dumps(data, default=str).encode(encoding)
    elif isinstance(data, List):
        encoded_data = json.dumps(data, default=str).encode(encoding)
    else:
        logger.warning(f"Unknown data type to encode SSE: {type(data)}")
        encoded_data = str(data).encode(encoding)
    return b"data: " + encoded_data + b"\n\n"
