from fastapi import APIRouter

from app.api.v1.endpoints import items, rag, storage, utils

api_router = APIRouter()
api_router.include_router(items.router)
api_router.include_router(storage.router)
api_router.include_router(utils.router)
api_router.include_router(rag.router)
