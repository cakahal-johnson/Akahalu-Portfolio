# Akahalu Portfolio Frontend

The frontend application for **Akahalu Portfolio**, built with Next.js, React, TypeScript, and Tailwind CSS.

It provides both:

* the public portfolio website;
* the protected administration application.

The application communicates with the FastAPI backend while maintaining a clear separation between browser-safe API configuration and server-only backend communication.

---

## Stack

Current frontend stack:

```text
Next.js 16.2.12
React 19.2.4
TypeScript
Tailwind CSS 4
shadcn-based UI components
TanStack Query
Axios
Zod
lucide-react
react-icons
pnpm 11.18.0
```

The package manager is pinned through `package.json`.

Use:

```bash
pnpm
```

rather than npm/yarn for normal project development.

---

# Application Surfaces

## Public Portfolio

Main public routes include:

```text
/
/about
/projects
/projects/[slug]
/experience
/contact
```

The public application consumes public portfolio APIs for:

* profile;
* projects;
* categories;
* technologies;
* professional experience;
* contact submissions.

---

## Administration

The protected administrator application includes areas such as:

```text
/admin
/admin/profile
/admin/projects
/admin/categories
/admin/technologies
/admin/experience
/admin/inquiries
/admin/users
```

Authentication routes include:

```text
/admin/login
/admin/forgot-password
/admin/reset-password
```

Administrative access remains subject to backend role and permission enforcement.

---

# Architecture

The frontend uses the Next.js App Router.

Conceptually:

```text
frontend/app/
├── (site)/
├── (admin)/
└── api/
```

The application separates:

```text
public website rendering
administrator UI
browser-facing BFF routes
server-only FastAPI communication
```

---

# Public Data Flow

Public server-rendered data follows:

```text
Browser
   |
   v
Next.js page/server component
   |
   v
frontend data/service layer
   |
   v
FastAPI /api/v1
   |
   v
PostgreSQL
```

Server-side requests use the internal/server backend configuration.

---

# Administrator BFF

Protected administrator requests use a Backend-for-Frontend pattern:

```text
Admin browser
    |
    v
Next.js /api/admin/*
    |
    v
FastAPI /api/v1/admin/*
```

Authentication routes use:

```text
/api/admin-auth/*
```

Examples:

```text
/api/admin-auth/login
/api/admin-auth/logout
/api/admin-auth/refresh
/api/admin-auth/session
```

The browser does not need direct access to the FastAPI bearer token.

---

# Authentication Cookies

Administrator access and refresh tokens are stored using HttpOnly cookies.

This means normal browser JavaScript cannot directly read the raw credentials.

FastAPI remains authoritative for:

```text
credential validation
access-token issuance
refresh rotation
session validation
refresh reuse detection
authorization
```

Frontend permission checks are user-interface controls, not replacements for backend authorization.

---

# Environment Variables

Create:

```text
frontend/.env.local
```

from:

```text
frontend/.env.example
```

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

---

# Public vs Server-Only Configuration

Variables beginning with:

```text
NEXT_PUBLIC_
```

may become browser-visible.

They must never contain secrets.

`BACKEND_API_URL` is server-only.

Production Docker configuration uses:

```text
BACKEND_API_URL=http://backend:8000/api/v1
```

for internal Next.js-to-FastAPI communication.

A same-domain public deployment can use:

```text
NEXT_PUBLIC_APP_URL=https://<domain>
NEXT_PUBLIC_API_URL=https://<domain>/api/v1
```

---

# Install Dependencies

From `frontend/`:

```bash
pnpm install
```

CI uses:

```bash
pnpm install --frozen-lockfile
```

to guarantee lockfile reproducibility.

---

# Run Development Server

```bash
pnpm dev
```

Open:

```text
http://localhost:3000
```

The local FastAPI backend is normally available at:

```text
http://127.0.0.1:8000
```

---

# Quality Checks

Run ESLint:

```bash
pnpm lint
```

Run TypeScript:

```bash
pnpm exec tsc --noEmit
```

Run the production build:

```bash
pnpm build
```

All three should succeed before a frontend change is considered release-ready.

---

# Production Build

`next.config.ts` uses:

```text
output: "standalone"
poweredByHeader: false
```

The production build must create:

```text
.next/standalone
```

The Docker runtime uses this standalone output.

---

# Backend-Independent Builds

A key deployment requirement is that:

```bash
pnpm build
```

must succeed even when FastAPI is unavailable.

Public data loaders provide safe fallback states where necessary.

This prevents frontend image creation from requiring:

```text
FastAPI
PostgreSQL
Redis
```

to be live during the build stage.

CI enforces this behavior by building the frontend without starting FastAPI.

---

# Production Container

The frontend production image is defined by:

```text
infrastructure/docker/frontend.Dockerfile
```

from the repository root.

The multi-stage build:

```text
installs frozen dependencies
        ↓
builds Next.js
        ↓
copies standalone output
        ↓
runs a minimal production server
```

The runtime user is:

```text
nextjs
```

rather than root.

The internal application port is:

```text
3000
```

It is not directly host-published by the production Compose stack.

---

# Frontend Health Endpoint

The application exposes:

```http
GET /api/health
```

This confirms the Next.js runtime independently from FastAPI.

Expected response identifies:

```text
portfolio-web
```

---

# Nginx Routing

Production Nginx routes:

```text
/api/v1/*       -> FastAPI
everything else -> Next.js
```

Therefore these routes remain Next.js-owned:

```text
/api/admin/*
/api/admin-auth/*
```

This distinction is essential to the administrator BFF architecture.

---

# pnpm Build-Script Policy

The project uses an explicit pnpm dependency build-script allowlist.

Current approved packages:

```text
sharp@0.34.5
unrs-resolver@1.12.2
```

Configuration:

```text
frontend/pnpm-workspace.yaml
```

Do not globally enable arbitrary dependency install/build scripts.

Review additional packages before adding them to the allowlist.

---

# Frontend CI

Workflow:

```text
.github/workflows/frontend-ci.yml
```

The frontend CI pipeline runs:

```text
pnpm install --frozen-lockfile
pnpm lint
pnpm exec tsc --noEmit
pnpm build
```

and verifies that:

```text
.next/standalone
```

was generated.

---

# Error Handling

Public pages are designed to degrade gracefully when portfolio data is temporarily unavailable.

Examples include:

```text
profile unavailable
empty project list
empty featured projects
empty experience list
empty featured experience
```

Administrative operations should instead surface meaningful authentication, authorization, validation, and backend errors.

A public fallback must not be used to conceal a protected administrative failure.

---

# Security Principles

Frontend changes should preserve these rules:

1. Do not place backend secrets in `NEXT_PUBLIC_*` variables.
2. Keep `BACKEND_API_URL` server-only.
3. Do not store backend access/refresh tokens in localStorage.
4. Keep administrator BFF routes within Next.js.
5. Treat FastAPI authorization as authoritative.
6. Keep public and administrative data paths separate.
7. Preserve backend-independent production builds.
8. Keep dependency build-script approval explicit.
9. Validate TypeScript and production builds before release.

---

# Related Documentation

From the repository root:

```text
docs/architecture/frontend-architecture.md
docs/architecture/system-overview.md
docs/api/api-reference.md
docs/security/authentication.md
docs/security/authorization.md
docs/deployment/environment-variables.md
docs/deployment/production-runbook.md
```

Root project documentation:

```text
README.md
```
