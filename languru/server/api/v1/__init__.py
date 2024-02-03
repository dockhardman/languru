from fastapi import APIRouter

from languru.server.api.v1.chat import router as chat_router

router = APIRouter()


router.include_router(router=chat_router)
