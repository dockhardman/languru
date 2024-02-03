from fastapi import APIRouter

from languru.server.api.v1.chat import router as chat_router
from languru.server.api.v1.model import router as model_router

router = APIRouter()


router.include_router(router=chat_router, tags=["chat"])
router.include_router(router=model_router, tags=["model"])
