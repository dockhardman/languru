import asyncio
import time
from contextlib import asynccontextmanager
from typing import Sequence, Text, cast

import httpx
from fastapi import FastAPI
from openai.types import Model

from languru.action.base import ModelDeploy
from languru.action.utils import load_action
from languru.server.config import init_logger_config, init_paths


async def register_model_periodically(model: Model, period: int, agent_base_url: Text):
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_base_url}/v1/models/register",
                    json=model.model_dump(),
                )
                response.raise_for_status()
                await asyncio.sleep(float(period))
        except httpx.HTTPError as e:
            logger.error(f"Failed to register model '{model.id}': {e}")
            await asyncio.sleep(float(settings.MODEL_REGISTER_FAIL_PERIOD))
