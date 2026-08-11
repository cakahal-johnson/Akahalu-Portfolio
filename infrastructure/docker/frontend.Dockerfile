# syntax=docker/dockerfile:1.7

ARG NODE_VERSION=22.21.0


# ============================================================
# Base
# ============================================================

FROM node:${NODE_VERSION}-alpine AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"
ENV NEXT_TELEMETRY_DISABLED=1

RUN corepack enable \
    && corepack prepare \
        pnpm@11.18.0 \
        --activate


# ============================================================
# Dependencies
# ============================================================

FROM base AS dependencies

WORKDIR /app

COPY frontend/package.json ./
COPY frontend/pnpm-lock.yaml ./
COPY frontend/pnpm-workspace.yaml ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install \
        --frozen-lockfile


# ============================================================
# Builder
# ============================================================

FROM base AS builder

WORKDIR /app

COPY \
    --from=dependencies \
    /app/node_modules \
    ./node_modules

COPY frontend/ ./

RUN mkdir -p public

ARG NEXT_PUBLIC_APP_URL
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_API_TIMEOUT_MS=15000

ENV NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL}"
ENV NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}"
ENV NEXT_PUBLIC_API_TIMEOUT_MS="${NEXT_PUBLIC_API_TIMEOUT_MS}"

# Build-time server data access must not depend on another
# running container. Public data loaders provide safe fallbacks
# while FastAPI is unavailable during image creation.
ENV BACKEND_API_URL="http://127.0.0.1:8000/api/v1"

RUN pnpm build


# ============================================================
# Runtime
# ============================================================

FROM node:${NODE_VERSION}-alpine AS runtime

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME="0.0.0.0"
ENV PORT=3000

WORKDIR /app

RUN addgroup \
        --system \
        --gid 1001 \
        nodejs \
    && adduser \
        --system \
        --uid 1001 \
        nextjs

COPY \
    --from=builder \
    --chown=nextjs:nodejs \
    /app/public \
    ./public

COPY \
    --from=builder \
    --chown=nextjs:nodejs \
    /app/.next/standalone \
    ./

COPY \
    --from=builder \
    --chown=nextjs:nodejs \
    /app/.next/static \
    ./.next/static

RUN mkdir -p .next/cache \
    && chown -R \
        nextjs:nodejs \
        .next

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD ["node","-e","fetch('http://127.0.0.1:3000/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]

CMD ["node","server.js"]