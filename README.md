# 🚀 Akahalu Portfolio

> A production-oriented full-stack portfolio and content-management platform built with **Next.js**, **FastAPI**, **PostgreSQL**, and **Redis**.

[![Backend CI](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/backend-ci.yml/badge.svg?branch=feature/account-lifecycle)](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/frontend-ci.yml/badge.svg?branch=feature/account-lifecycle)](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/frontend-ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Next.js](https://img.shields.io/badge/Next.js-16.2.12-black)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Status

**Version 1 Web Platform:** application and container deployment ready.

The project currently has:

* complete FastAPI backend;
* complete Next.js public portfolio;
* complete protected administration platform;
* PostgreSQL persistence and Alembic migrations;
* Redis infrastructure;
* secure authentication and RBAC;
* production Docker images;
* Nginx reverse proxy;
* backend and frontend GitHub Actions CI;
* deployment and architecture documentation.

The remaining work before a public production launch is primarily operational:

* select and provision the production host;
* configure the production domain and DNS;
* configure HTTPS/TLS;
* establish production backup and restore procedures;
* configure monitoring and alerting;
* perform the final production deployment and smoke test.

---

# Overview

Akahalu Portfolio is more than a static developer website.

It combines a public professional portfolio with a secure administration system for managing:

* profile information;
* projects;
* project categories;
* technologies;
* project media;
* project links;
* professional experience;
* contact inquiries;
* users;
* roles and permissions.

The architecture is designed to demonstrate practical full-stack engineering across application development, API design, authentication, database design, containerization, continuous integration, and production deployment.

---

# Core Features

## Public Portfolio

The public application includes:

* professional profile and biography;
* featured projects;
* complete project directory;
* project detail pages;
* project-category filtering;
* technology filtering;
* professional experience;
* featured experience;
* responsive navigation;
* contact form;
* SEO metadata;
* loading, unavailable, and empty states.

Public portfolio data is filtered server-side so private, unpublished, inactive, or soft-deleted content is not exposed.

---

## Administration Platform

The protected administration application provides:

* dashboard;
* profile management;
* project management;
* category management;
* technology management;
* project media management;
* project link management;
* professional experience management;
* contact inquiry management;
* user administration;
* RBAC administration;
* visibility controls;
* featured-content controls;
* soft deletion and restoration;
* search, filtering, sorting, and pagination.

---

## Authentication and Security

Authentication includes:

* Argon2 password hashing;
* short-lived JWT access tokens;
* refresh-token rotation;
* refresh-token families;
* refresh-token reuse detection;
* database-backed sessions;
* session revocation;
* current-session logout;
* logout-all;
* failed-login tracking;
* temporary account lockout;
* email verification;
* password-reset lifecycle;
* account activation/deactivation handling.

Administrator browser authentication uses a Next.js Backend-for-Frontend layer.

Backend credentials are stored in **HttpOnly cookies** instead of browser local storage.

FastAPI remains the authoritative authentication and authorization boundary.

---

## Role-Based Access Control

Current system roles:

```text
super_admin
admin
editor
viewer
```

The synchronized identity catalogue currently contains **17 permissions** across:

* projects;
* profile;
* experience;
* contact inquiries;
* users;
* RBAC.

Protected FastAPI endpoints enforce permissions server-side.

Frontend navigation and action visibility improve user experience but do not replace backend authorization.

---

# Architecture

Production traffic follows this model:

```text
                        Internet
                           |
                           v
                        Nginx
                     /           \
                    /             \
                   v               v
              Next.js           FastAPI
                 |                 |
                 | BFF             +--------+
                 +------------->   |        |
                                   v        v
                              PostgreSQL   Redis
```

Production routing:

```text
/api/v1/*        -> FastAPI
everything else  -> Next.js
```

Next.js BFF routes remain inside Next.js:

```text
/api/admin/*
/api/admin-auth/*
```

Only Nginx is intended to be publicly exposed.

PostgreSQL, Redis, FastAPI, and Next.js remain internal application services.

---

# Backend Architecture

Backend request flow follows the application's layered architecture:

```text
FastAPI endpoint
      ↓
Pydantic request/response schemas
      ↓
Service layer
      ↓
Repository / persistence layer
      ↓
SQLAlchemy models
      ↓
PostgreSQL
```

Main backend source:

```text
backend/app/
├── api/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── security/
├── services/
└── main.py
```

Schema evolution is managed through Alembic rather than runtime table creation.

---

# Frontend Architecture

The frontend uses the Next.js App Router and contains two primary surfaces:

```text
Public portfolio
Protected administration
```

Server-side portfolio requests use a server-only backend address.

Administrator requests use Next.js BFF routes so the browser does not need direct access to backend bearer tokens.

The production frontend build uses:

```text
output: "standalone"
```

and has been validated to build successfully even when FastAPI is unavailable.

---

# Technology Stack

## Backend

* Python 3.13
* FastAPI
* Pydantic
* Pydantic Settings
* SQLAlchemy 2
* Alembic
* PostgreSQL 17
* Psycopg
* Redis 8
* PyJWT
* pwdlib / Argon2
* Uvicorn
* HTTPX
* Structlog
* Tenacity
* uv

## Frontend

* Next.js 16.2.12
* React 19.2.4
* TypeScript
* Tailwind CSS 4
* shadcn-based UI components
* TanStack Query
* Axios
* Zod
* lucide-react
* react-icons
* pnpm 11.18.0

## Quality

* pytest
* pytest-asyncio
* pytest-cov
* Ruff
* mypy
* ESLint
* TypeScript compiler
* GitHub Actions

## Infrastructure

* Docker
* Docker Compose
* Nginx
* PostgreSQL
* Redis
* GitHub Actions
* Git

---

# Repository Structure

```text
Akahalu-Portfolio/
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
│
├── backend/
│   ├── app/
│   ├── migrations/
│   ├── scripts/
│   ├── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── config/
│   ├── lib/
│   ├── services/
│   ├── types/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── pnpm-workspace.yaml
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── postgres/
│   └── production.env.example
│
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── database/
│   ├── deployment/
│   └── security/
│
├── docker-compose.yml
├── docker-compose.production.yml
└── README.md
```

---

# Documentation

Detailed technical documentation is available under [`docs/`](docs/).

## Architecture

* [System Overview](docs/architecture/system-overview.md)
* [Backend Architecture](docs/architecture/backend-architecture.md)
* [Frontend Architecture](docs/architecture/frontend-architecture.md)

## API

* [API Reference](docs/api/api-reference.md)

## Database

* [Data Model](docs/database/data-model.md)
* [Migrations](docs/database/migrations.md)

## Security

* [Authentication](docs/security/authentication.md)
* [Authorization](docs/security/authorization.md)

## Deployment

* [Deployment Readiness](docs/deployment/deployment-readiness.md)
* [Environment Variables](docs/deployment/environment-variables.md)
* [Production Runbook](docs/deployment/production-runbook.md)

---

# API Overview

The FastAPI application is versioned beneath:

```text
/api/v1
```

The current generated OpenAPI contract contains:

```text
73 paths
99 HTTP operations
127 OpenAPI schemas
```

Primary API groups include:

```text
Health
Authentication
Account lifecycle
Public contact
Public portfolio
Admin contact inquiries
Admin portfolio
Admin users
RBAC
```

For the complete route and permission reference, see:

[docs/api/api-reference.md](docs/api/api-reference.md)

---

# Health Endpoints

```http
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

Readiness checks:

```text
PostgreSQL
Redis
```

The Next.js application also exposes:

```http
GET /api/health
```

Production Nginx provides:

```http
GET /healthz
```

---

# Local Development

## Prerequisites

Install:

* Git
* Docker Desktop
* Python 3.13
* uv
* Node.js 22
* pnpm 11

Clone:

```bash
git clone https://github.com/cakahal-johnson/Akahalu-Portfolio.git
cd Akahalu-Portfolio
```

---

# Start Local Infrastructure

From the repository root:

```bash
docker compose up -d
```

Inspect:

```bash
docker compose ps
```

Stop:

```bash
docker compose down
```

---

# Backend Setup

Move into the backend:

```bash
cd backend
```

Install locked dependencies:

```bash
uv sync
```

Create the local environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Update the local values as required.

Apply migrations:

```bash
uv run alembic upgrade head
```

Synchronize system roles and permissions without creating an administrator:

```bash
uv run python -m scripts.seed_identity --skip-admin
```

Run FastAPI:

```bash
uv run uvicorn app.main:app --reload
```

Development backend:

```text
http://127.0.0.1:8000
```

Development Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

From the repository root:

```bash
cd frontend
```

Install dependencies:

```bash
pnpm install
```

Create the local environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env.local
```

macOS/Linux:

```bash
cp .env.example .env.local
```

Typical local configuration:

```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
NEXT_PUBLIC_API_TIMEOUT_MS=15000
BACKEND_API_URL=http://127.0.0.1:8000/api/v1
```

Run:

```bash
pnpm dev
```

Frontend:

```text
http://localhost:3000
```

---

# Backend Validation

From `backend/`:

```bash
uv run ruff check app scripts tests
```

```bash
uv run mypy app scripts tests
```

```bash
uv run pytest -q
```

Current validated local full-suite result:

```text
391 passed
```

Verify Alembic head:

```bash
uv run alembic heads
```

Current migration head:

```text
17f167659ec9
```

The migration graph currently has one head.

---

# Frontend Validation

From `frontend/`:

```bash
pnpm lint
```

```bash
pnpm exec tsc --noEmit
```

```bash
pnpm build
```

Production builds must generate:

```text
.next/standalone
```

The frontend production build is intentionally backend-independent.

---

# Continuous Integration

The repository contains two GitHub Actions workflows.

## Backend CI

Runs:

```text
uv sync --locked
Ruff
mypy
single-Alembic-head verification
fresh PostgreSQL migration
pytest
```

PostgreSQL 17 is provisioned as a CI service.

## Frontend CI

Runs:

```text
pnpm install --frozen-lockfile
ESLint
TypeScript
Next.js production build
standalone-output verification
```

The frontend CI workflow does not start FastAPI.

Both initial remote workflow runs completed successfully.

---

# Production Containers

Production infrastructure is defined in:

```text
docker-compose.production.yml
```

Services:

```text
postgres
redis
migrate
identity-bootstrap
backend
frontend
nginx
```

Expected steady state:

```text
postgres             healthy
redis                healthy
migrate              exited (0)
identity-bootstrap   exited (0)
backend              healthy
frontend             healthy
nginx                healthy
```

`migrate` and `identity-bootstrap` are intentionally one-shot services.

---

# Production Environment

Start from:

```text
infrastructure/production.env.example
```

Create the real untracked file:

```text
infrastructure/production.env
```

Production secrets include:

```text
POSTGRES_PASSWORD
REDIS_PASSWORD
JWT_SECRET_KEY
CONTACT_HASH_SECRET_KEY
```

Never commit the real production environment file.

See:

[Environment Variables](docs/deployment/environment-variables.md)

---

# Production Security

Production hardening includes:

* `DEBUG=false`;
* restricted CORS origins;
* Trusted Host middleware;
* no wildcard trusted hosts;
* API documentation disabled;
* private PostgreSQL and Redis networking;
* non-root backend runtime;
* non-root frontend runtime;
* HttpOnly administrator authentication cookies;
* secure-cookie behavior in production;
* Nginx security response headers;
* externalized secrets.

Validated Nginx headers include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

# Database

PostgreSQL uses the extensions:

```text
uuid-ossp
pgcrypto
citext
```

Schema changes are managed with Alembic.

Current migration chain:

```text
616a4a5910c3
      ↓
1d1a0aa75236
      ↓
fc710990420c
      ↓
e518f89e76f5
      ↓
291b9552d692
      ↓
a7e354695851
      ↓
17f167659ec9
```

See:

* [Data Model](docs/database/data-model.md)
* [Migrations](docs/database/migrations.md)

---

# Production Deployment

The production deployment flow is:

```text
PostgreSQL healthy
      ↓
Alembic migration
      ↓
Identity bootstrap
      ↓
FastAPI healthy
      ↓
Next.js healthy
      ↓
Nginx healthy
```

A full operational procedure is documented in:

[Production Runbook](docs/deployment/production-runbook.md)

Do not use:

```bash
docker compose down -v
```

against production or production-like data unless volume destruction is explicitly intended.

---

# Current Deployment Readiness

Completed:

* [x] Public portfolio
* [x] Protected admin platform
* [x] Authentication
* [x] RBAC
* [x] PostgreSQL
* [x] Redis
* [x] Alembic migration chain
* [x] Production-safe backend configuration
* [x] Backend-independent frontend build
* [x] Production backend Docker image
* [x] Production frontend Docker image
* [x] Production Compose topology
* [x] Nginx reverse proxy
* [x] Security headers
* [x] Non-root application containers
* [x] Health/readiness checks
* [x] Identity bootstrap
* [x] Backend CI
* [x] Frontend CI
* [x] Technical deployment documentation

Remaining before public production launch:

* [ ] Production hosting
* [ ] DNS/domain
* [ ] HTTPS/TLS
* [ ] Backup and restore implementation
* [ ] Monitoring and alerting
* [ ] Final production administrator initialization
* [ ] Final public deployment
* [ ] Final production smoke verification

---

# Version Strategy

## Version 1 — Web Platform

Version 1 establishes the complete web portfolio platform and reusable API foundation.

Current work is focused on final production operations and deployment.

## Future Mobile Platform

A future phase may reuse the FastAPI backend for native applications such as:

* Android;
* iOS.

Potential capabilities include:

* portfolio browsing;
* secure mobile authentication;
* selected administrative functions;
* offline support;
* notifications;
* deep linking;
* resume sharing.

These remain future roadmap items rather than current Version 1 functionality.

---

# Development Principles

Changes should preserve:

* separation of API, schema, service, repository, and model responsibilities;
* backend-enforced authentication and authorization;
* explicit database migrations;
* TypeScript contract consistency;
* backend-independent frontend builds;
* Git-ignored secrets;
* test coverage for important behavior;
* CI validation before deployment.

---

# Contribution

This is primarily a personal portfolio engineering project.

Technical feedback and carefully scoped contributions are welcome.

Before committing changes:

```text
Backend:
Ruff
mypy
pytest

Frontend:
ESLint
TypeScript
production build
```

Do not commit secrets or environment files containing real credentials.

---

# Author

**Akahalu Johnson**

Software Engineer · Backend Developer · Full-Stack Developer

GitHub:

https://github.com/cakahal-johnson

Repository:

https://github.com/cakahal-johnson/Akahalu-Portfolio

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
