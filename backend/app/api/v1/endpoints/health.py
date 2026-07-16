from datetime import UTC, datetime
from typing import Literal

import redis.asyncio as redis_async
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text

from app.core.config import settings
from app.db.session import async_session_factory


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    service: str
    environment: str
    timestamp: datetime


class ReadinessDependencies(BaseModel):
    database: Literal["healthy", "unhealthy"]
    redis: Literal["healthy", "unhealthy"]


class ReadinessResponse(HealthResponse):
    dependencies: ReadinessDependencies


@router.get(
    "",
    response_model=HealthResponse,
    summary="Check general API health",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="portfolio-api",
        environment=settings.environment,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/live",
    response_model=HealthResponse,
    summary="Check whether the API process is alive",
)
async def liveness_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="portfolio-api",
        environment=settings.environment,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Check whether application dependencies are ready",
)
async def readiness_check() -> ReadinessResponse:
    database_status: Literal["healthy", "unhealthy"] = "unhealthy"
    redis_status: Literal["healthy", "unhealthy"] = "unhealthy"

    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))

        database_status = "healthy"
    except Exception:
        database_status = "unhealthy"

    redis_client = redis_async.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    try:
        await redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    finally:
        await redis_client.aclose()

    if database_status == "unhealthy" or redis_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "portfolio-api",
                "environment": settings.environment,
                "dependencies": {
                    "database": database_status,
                    "redis": redis_status,
                },
            },
        )

    return ReadinessResponse(
        status="healthy",
        service="portfolio-api",
        environment=settings.environment,
        timestamp=datetime.now(UTC),
        dependencies=ReadinessDependencies(
            database=database_status,
            redis=redis_status,
        ),
    )
