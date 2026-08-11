# syntax=docker/dockerfile:1.7

# ============================================================
# Akahalu Portfolio Backend
# ============================================================

FROM python:3.13-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.29 \
    /uv \
    /uvx \
    /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project


# ============================================================
# Runtime
# ============================================================

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:${PATH}"

RUN groupadd \
        --system \
        --gid 10001 \
        appuser \
    && useradd \
        --system \
        --uid 10001 \
        --gid appuser \
        --home-dir /home/appuser \
        --create-home \
        appuser

WORKDIR /app

COPY \
    --from=builder \
    --chown=appuser:appuser \
    /app/.venv \
    /app/.venv

COPY \
    --chown=appuser:appuser \
    backend/app \
    ./app

COPY \
    --chown=appuser:appuser \
    backend/migrations \
    ./migrations

COPY \
    --chown=appuser:appuser \
    backend/scripts \
    ./scripts

COPY \
    --chown=appuser:appuser \
    backend/alembic.ini \
    ./alembic.ini

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD ["python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/ready', timeout=3).read()"]

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers","--forwarded-allow-ips=*"]