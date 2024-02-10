from fastapi import APIRouter

from languru.server.api.v1.chat import router as chat_router
from languru.server.api.v1.completions import router as completions_router
from languru.server.api.v1.embeddings import router as embeddings_router
from languru.server.api.v1.model import router as model_router
from languru.server.api.v1.moderations import router as moderations_router

router = APIRouter()


router.include_router(router=model_router, tags=["model"])
router.include_router(router=chat_router, tags=["chat"])
router.include_router(router=completions_router, tags=["completions"])
router.include_router(router=embeddings_router, tags=["embeddings"])
router.include_router(router=moderations_router, tags=["moderations"])
