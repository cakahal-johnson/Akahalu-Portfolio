from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import (
    TrustedHostMiddleware,
)

from app.api.router import api_router
from app.core.config import settings


docs_url = "/docs" if settings.api_docs_are_enabled else None

redoc_url = "/redoc" if settings.api_docs_are_enabled else None

openapi_url = "/openapi.json" if settings.api_docs_are_enabled else None


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=(settings.trusted_hosts),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
    ],
)


@app.get(
    "/",
    tags=["Root"],
    summary="API root",
)
async def root() -> dict[
    str,
    str,
]:
    return {
        "message": "Akahalu Portfolio API",
        "status": "running",
        "documentation": ("/docs" if (settings.api_docs_are_enabled) else "disabled"),
        "health": "/api/v1/health",
    }


app.include_router(api_router)
