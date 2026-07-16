from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get(
    "/",
    tags=["Root"],
    summary="API root",
)
async def root() -> dict[str, str]:
    return {
        "message": "Akahalu Portfolio API",
        "status": "running",
        "documentation": "/docs",
        "health": "/api/v1/health",
    }


app.include_router(api_router)
