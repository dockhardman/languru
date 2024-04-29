from typing import Text, cast

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from openai.types.audio import Transcription, Translation
from pyassorted.asyncio.executor import run_func, run_generator

from languru.exceptions import ModelNotFound
from languru.server.config import (
    AgentSettings,
    AppType,
    LlmSettings,
    ServerBaseSettings,
)
from languru.server.deps.common import app_settings
from languru.server.utils.common import get_value_from_app
from languru.types.images import (
    ImagesGenerationsRequest,
    ImagesEditRequest,
    ImagesVariationsRequest,
)

router = APIRouter()
