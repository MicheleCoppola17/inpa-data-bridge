from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import db_ping
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> JSONResponse | HealthResponse:
    settings = get_settings()
    db_up = await db_ping()

    payload = HealthResponse(
        status="ok" if db_up else "degraded",
        service=settings.app_name,
        version=settings.app_version,
        db="up" if db_up else "down",
    )

    if db_up:
        return payload

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload.model_dump(),
    )
