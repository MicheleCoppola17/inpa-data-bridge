from fastapi import APIRouter

from app.api.v1.endpoints.exams import router as exams_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.sync import router as sync_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(exams_router)
api_router.include_router(sync_router)
