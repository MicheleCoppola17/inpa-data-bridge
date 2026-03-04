import asyncio

from fastapi import APIRouter, status

from app.schemas.exam import SyncStatusResponse
from app.services.sync_runtime import sync_runtime

router = APIRouter(prefix="/internal/sync", tags=["sync"])


@router.get("/status", response_model=SyncStatusResponse)
async def sync_status() -> SyncStatusResponse:
    return sync_runtime.build_status()


@router.post("/run", status_code=status.HTTP_202_ACCEPTED, response_model=SyncStatusResponse)
async def trigger_sync() -> SyncStatusResponse:
    if not sync_runtime.is_running():
        asyncio.create_task(sync_runtime.run_once())
    return sync_runtime.build_status()
