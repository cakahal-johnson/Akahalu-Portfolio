# 🚀 Akahalu Portfolio

> A production-oriented full-stack portfolio and content-management platform built with **Next.js**, **FastAPI**, **PostgreSQL**, **Redis**, and a **Kotlin Multiplatform mobile application**.

[![Backend CI](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/backend-ci.yml/badge.svg?branch=feature/account-lifecycle)](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/frontend-ci.yml/badge.svg?branch=feature/account-lifecycle)](https://github.com/cakahal-johnson/Akahalu-Portfolio/actions/workflows/frontend-ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Next.js](https://img.shields.io/badge/Next.js-16.2.12-black)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791)
![Kotlin](https://img.shields.io/badge/Kotlin-2.4.20-7F52FF)
![Compose Multiplatform](https://img.shields.io/badge/Compose%20Multiplatform-1.11.1-4285F4)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Status

**Web Platform:** application and container deployment ready.

**Mobile Platform:** Android application M-12 complete and validated on a physical Android 16 device.

**Overall Project:** active development.

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
* deployment and architecture documentation;
* Kotlin Multiplatform mobile application foundation;
* shared mobile presentation, domain, data, networking, and caching layers;
* Android portfolio browsing experience;
* project detail and navigation experience;
* professional experience integration;
* technology and skills integration;
* profile and contact integration;
* project media/gallery integration;
* Android 16 physical-device validation.

The remaining web-platform work before a public production launch is primarily operational:

* select and provision the production host;
* configure the production domain and DNS;
* configure HTTPS/TLS;
* establish production backup and restore procedures;
* configure monitoring and alerting;
* perform the final production deployment and smoke test.

The remaining mobile work is focused on:

* Android UX and production polish;
* accessibility and interaction refinement;
* performance inspection;
* production configuration;
* Android release readiness;
* release signing;
* release APK/AAB generation;
* final physical-device regression testing.

---

# Mobile Application

The repository contains a Kotlin Multiplatform mobile application that consumes the same versioned FastAPI portfolio API used by the web platform.

The mobile application is being developed as a production-oriented companion to the web portfolio, with shared presentation, domain, data, networking, and caching layers.

The current Android application has completed the foundation, API integration, portfolio presentation, project navigation, application shell, experience, skills/technologies, profile/contact, project media/gallery, and Android application completion milestones.

## Mobile Technology Stack

* Kotlin 2.4.20
* Kotlin Multiplatform
* Compose Multiplatform 1.11.1
* Compose Material 3
* Ktor 3.5.2
* Kotlin Serialization
* Kotlin Coroutines
* Coil 3.3.0
* Android SDK 36
* Android 16 physical-device validation

## Mobile Architecture

The mobile application follows a layered architecture:

```text
Presentation
      ↓
Domain
      ↓
Data
      ↓
Network / Cache
````

Responsibilities remain separated across the layers:

```text
Presentation
    ↓
UI, screens, navigation, state, loading and error presentation

Domain
    ↓
Application models and domain-facing contracts

Data
    ↓
Repositories, API integration, DTO mapping and cache coordination

Network / Cache
    ↓
Ktor HTTP client, serialization, remote API and local caching
```

The mobile application reuses the existing FastAPI portfolio API rather than introducing a separate mobile backend.

---

# Mobile Development Milestones

The mobile roadmap currently contains:

```text
M-1  KMP Foundation                         ✅ Complete
M-2  Architecture / Design System          ✅ Complete
M-3  Networking Foundation                 ✅ Complete
M-4  Portfolio API Data Layer              ✅ Complete
M-5  Portfolio Presentation Foundation     ✅ Complete
M-6  Project Detail / Navigation           ✅ Complete
M-7  Application Shell / Navigation        ✅ Complete
M-8  Experience Integration                ✅ Complete
M-9  Skills / Technologies                 ✅ Complete
M-10A Profile / Contact Read               ✅ Complete
M-10B Contact Message Submission           ✅ Complete
M-11 Project Media / Gallery               ✅ Complete
M-12 Android Application Completion        ✅ Complete
M-13 Android UX / Production Polish        ⏳ Next
M-14 Android Release Readiness             ⏳ Planned
```

## M-12 Android Application Completion

M-12 completed the Android portfolio experience and included:

* Android dependency alignment;
* Compose Multiplatform compatibility updates;
* loading skeletons;
* AlphaDev branding and logo integration;
* responsive hero presentation;
* application-shell navigation polish;
* system inset handling;
* Android resource compatibility;
* project browsing;
* project detail navigation;
* portfolio API integration;
* experience and technology presentation;
* profile/contact presentation;
* project media/gallery presentation;
* physical Android 16 validation.

The Android application was validated on a physical Android 16 device.

Final runtime validation completed without:

```text
FATAL EXCEPTION
NoSuchMethodError
IllegalStateException
```

The application exited cleanly after the final validation run.

---

# M-13 Android UX / Production Polish

The next mobile milestone focuses on production-quality user experience rather than introducing a new architectural layer.

Planned M-13 work:

```text
M-13 Android UX / Production Polish
├── Responsive layout inspection
├── Typography / spacing consistency
├── Dark / light theme verification
├── Navigation UX polish
├── Error / empty / unavailable states
├── Image loading / caching UX
├── Accessibility review
├── Android back navigation
├── Touch targets / interaction polish
├── Performance inspection
└── Physical-device regression pass
```

M-13 changes should preserve the existing layered mobile architecture.

---

# M-14 Android Release Readiness

After M-13, Android release preparation will cover:

```text
M-14 Android Release Readiness
├── Application identity
├── Versioning
├── Launcher icon
├── Splash screen
├── Release signing
├── Release build
├── ProGuard / R8 inspection
├── Release APK / AAB
├── Privacy considerations
├── Production API configuration
├── Offline / cache behavior
├── Crash handling
└── Final release checklist
```

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

The platform also provides a Kotlin Multiplatform mobile application for consuming and presenting portfolio information through the same versioned API.

The architecture is designed to demonstrate practical full-stack engineering across application development, API design, authentication, database design, containerization, mobile development, continuous integration, and production deployment.

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

## Mobile Portfolio

The Android mobile application provides:

* portfolio browsing;
* featured project presentation;
* project detail navigation;
* project media/gallery presentation;
* professional experience;
* technologies and skills;
* profile information;
* contact information;
* contact message submission;
* loading states;
* unavailable and empty states;
* image loading and caching;
* responsive Compose UI;
* Android navigation.

The mobile application consumes the same FastAPI portfolio API as the web platform.

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

Mobile applications consume the versioned FastAPI API directly:

```text
Android / iOS
      |
      v
FastAPI /api/v1
      |
      +------ PostgreSQL
      |
      +------ Redis
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

# Mobile Architecture

The mobile application uses Kotlin Multiplatform and Compose Multiplatform.

The shared application is organized into:

```text
shared/
├── commonMain/
│   └── kotlin/
│       └── com/akahalu/portfolio/
│           ├── data/
│           ├── domain/
│           ├── presentation/
│           └── ...
```

The Android target consumes the shared implementation while retaining Android-specific configuration where required.

The mobile architecture is intentionally kept separate from the backend and web presentation layers while sharing the versioned API contract.

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

## Mobile

* Kotlin 2.4.20
* Kotlin Multiplatform
* Compose Multiplatform 1.11.1
* Compose Material 3
* Ktor 3.5.2
* Kotlin Serialization
* Kotlin Coroutines
* Coil 3.3.0
* Android SDK 36

## Quality

* pytest
* pytest-asyncio
* pytest-cov
* Ruff
* mypy
* ESLint
* TypeScript compiler
* Gradle
* Android instrumentation / physical-device validation
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
├── mobile/
│   ├── androidApp/
│   ├── shared/
│   ├── gradle/
│   ├── build.gradle.kts
│   ├── settings.gradle.kts
│   └── gradlew.bat
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
* JDK compatible with the Android/Kotlin build
* Android Studio for Android development

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

# Mobile Setup

From the repository root:

```bash
cd mobile
```

Verify Gradle:

Windows PowerShell:

```powershell
.\gradlew.bat --version
```

Build the Android application:

```powershell
.\gradlew.bat :androidApp:assembleDebug
```

Run Android unit tests:

```powershell
.\gradlew.bat :androidApp:testDebugUnitTest
```

Compile the shared Android source:

```powershell
.\gradlew.bat :shared:compileAndroidMain
```

Clean the mobile build:

```powershell
.\gradlew.bat clean
```

For physical-device development:

1. Enable Android Developer Options.
2. Enable USB debugging.
3. Connect the Android device.
4. Verify the device:

```powershell
adb devices
```

5. Build and install the debug application through Android Studio or Gradle.
6. Ensure the Android device can reach the development FastAPI host when testing against a local backend.

The Android application has been validated on a physical Android 16 device.

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

# Mobile Validation

From `mobile/`:

```powershell
.\gradlew.bat clean
```

```powershell
.\gradlew.bat :shared:compileAndroidMain
```

```powershell
.\gradlew.bat :androidApp:testDebugUnitTest
```

```powershell
.\gradlew.bat :androidApp:assembleDebug
```

Mobile validation should include physical-device regression testing for major Android milestones.

M-12 was validated on Android 16 with no fatal runtime exception observed during final launch validation.

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

Mobile CI/release automation can be introduced as part of the Android release-readiness phase.

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

## Web Platform

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

## Mobile Platform

Completed:

* [x] Kotlin Multiplatform foundation
* [x] Compose Multiplatform foundation
* [x] Shared application architecture
* [x] Ktor networking
* [x] Kotlin Serialization
* [x] Portfolio API data layer
* [x] Portfolio presentation
* [x] Project details
* [x] Navigation
* [x] Application shell
* [x] Experience integration
* [x] Skills and technologies
* [x] Profile and contact read
* [x] Contact message submission
* [x] Project media/gallery
* [x] Android application completion
* [x] Android 16 physical-device validation

Next:

* [ ] Android UX / production polish
* [ ] Accessibility review
* [ ] Performance inspection
* [ ] Physical-device regression pass
* [ ] Android release configuration
* [ ] Release signing
* [ ] Release APK/AAB
* [ ] Final Android release validation

---

# Version Strategy

## Version 1 — Web Platform

Version 1 establishes the complete web portfolio platform and reusable API foundation.

The web platform is application and container deployment ready.

Final public release work is focused on production hosting, domain configuration, HTTPS/TLS, backups, monitoring, administrator initialization, and final deployment validation.

## Mobile Platform

The mobile platform is an active companion application built on the same versioned FastAPI API.

The current Android implementation has completed M-12 and is moving into M-13 Android UX / production polish.

The mobile platform roadmap includes:

* Android;
* iOS;
* portfolio browsing;
* secure mobile authentication;
* selected administrative functions;
* offline support;
* notifications;
* deep linking;
* resume sharing.

Features that have not yet been implemented remain roadmap items rather than current functionality.

---

# Development Principles

Changes should preserve:

* separation of API, schema, service, repository, and model responsibilities;
* separation of mobile presentation, domain, data, network, and cache responsibilities;
* backend-enforced authentication and authorization;
* explicit database migrations;
* TypeScript contract consistency;
* mobile API contract consistency;
* backend-independent frontend builds;
* Git-ignored secrets;
* test coverage for important behavior;
* CI validation before deployment;
* physical-device validation for significant Android changes.

Avoid introducing duplicate business logic between:

```text
Web
Mobile
Backend
```

The FastAPI API remains the authoritative portfolio data and authentication boundary.

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

Mobile:
Gradle compilation
unit tests
Android debug build
physical-device validation when appropriate
```

Do not commit secrets or environment files containing real credentials.

---

# Author

**Akahalu Johnson**

Software Engineer · Backend Developer · Full-Stack Developer

GitHub:

[https://github.com/cakahal-johnson](https://github.com/cakahal-johnson)

Repository:

[https://github.com/cakahal-johnson/Akahalu-Portfolio](https://github.com/cakahal-johnson/Akahalu-Portfolio)

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for details.


