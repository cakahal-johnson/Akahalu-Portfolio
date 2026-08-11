# Akahalu Portfolio — Deployment Readiness

## 1. Purpose

This document records the deployment-readiness state of Akahalu Portfolio.

It distinguishes between:

* application functionality that has already been implemented;
* infrastructure that has been validated locally;
* CI safeguards that have been validated remotely;
* operational work still required before a public production launch.

A successful Docker smoke test does not by itself mean the application has completed every production-operational requirement.

---

## 2. Current Readiness Status

The application has completed the following deployment-readiness phases:

```text
DR-1  Production configuration hardening       COMPLETE
DR-2  Production container infrastructure      COMPLETE
DR-3  Continuous integration                   COMPLETE
DR-4  Production documentation                 IN PROGRESS
```

The following major items remain outside the completed infrastructure work:

```text
Production hosting selection
Production domain and DNS
HTTPS/TLS configuration
Production backup/restore implementation
Production monitoring and alerting
Final release/deployment procedure
Production administrator initialization
Final public smoke test
```

---

## 3. Application Architecture

The validated production architecture is:

```text
Internet / Edge
      |
      v
   Nginx
   /   \
  /     \
 v       v
Next.js  FastAPI
            |
        +---+---+
        |       |
        v       v
   PostgreSQL  Redis
```

Routing is intentionally separated:

```text
/api/v1/*       -> FastAPI
all other paths -> Next.js
```

Next.js administrator BFF routes such as:

```text
/api/admin/*
/api/admin-auth/*
```

therefore continue to be served by Next.js.

---

## 4. Public Exposure Boundary

The production Compose stack does not publish application dependencies directly.

The validated service exposure is:

```text
nginx      -> host published
frontend   -> Docker internal only
backend    -> Docker internal only
postgres   -> Docker internal only
redis      -> Docker internal only
```

The default local production smoke configuration publishes:

```text
127.0.0.1:8080 -> nginx:80
```

This default is intentionally appropriate for local production-stack validation.

It is **not**, by itself, a complete public Internet deployment.

A real hosting environment must provide the final public network and HTTPS boundary.

---

## 5. Backend Production Configuration

The backend validates production settings during application initialization.

Production mode rejects unsafe configurations including:

```text
DEBUG=true
empty allowed-origin configuration
wildcard CORS origins
localhost development HTTP origins
empty trusted-host configuration
wildcard trusted hosts
```

Production configuration uses:

```text
ENVIRONMENT=production
DEBUG=false
API_DOCS_ENABLED=false
```

API documentation is disabled by default in production.

Validated production behavior:

```text
/docs         -> 404
/openapi.json -> 404
```

---

## 6. Trusted Hosts

Production trusted-host configuration must include every hostname legitimately used to reach FastAPI.

This can include:

```text
public portfolio domain
www portfolio domain
backend
localhost
127.0.0.1
```

The internal name:

```text
backend
```

is required for Docker-network communication from Next.js.

Loopback hosts are used by container health checks and local production-stack validation.

Wildcard trusted hosts are not permitted in production.

---

## 7. CORS

Production CORS configuration must contain only approved browser origins.

Example:

```text
https://portfolio.example.com
```

If the application is also intentionally served through:

```text
https://www.portfolio.example.com
```

that origin should be included explicitly if browser cross-origin behavior requires it.

The wildcard origin:

```text
*
```

is prohibited in production.

---

## 8. Frontend Production Configuration

Next.js uses standalone production output:

```text
output: "standalone"
```

The production image includes:

```text
.next/standalone
.next/static
public
```

The frontend container runs the generated standalone server using:

```text
node server.js
```

The production runtime user is:

```text
nextjs
```

rather than root.

---

## 9. Backend Production Container

The backend production container uses:

```text
Python 3.13
uv
Uvicorn
```

Dependencies are installed from the locked project dependency state.

The runtime container executes as:

```text
appuser
```

rather than root.

FastAPI listens internally on:

```text
0.0.0.0:8000
```

but the port is not published directly by the production Compose stack.

---

## 10. Frontend Build Independence

The frontend production image has been validated while FastAPI was unavailable.

During the build:

```text
backend unavailable
        |
        v
pnpm build
        |
        v
Next.js build succeeds
        |
        v
35/35 routes generated
        |
        v
.next/standalone created
```

This is an intentional deployment property.

Building a frontend image does not require:

```text
PostgreSQL
Redis
FastAPI
```

to be live.

Public data loaders degrade to safe fallback states where necessary.

---

## 11. PostgreSQL

Production uses:

```text
PostgreSQL 17 Alpine
```

Required extensions are:

```text
uuid-ossp
pgcrypto
citext
```

They are initialized by:

```text
infrastructure/postgres/init.sql
```

PostgreSQL data is persisted through a Docker volume.

The database port is not host-published by the production Compose stack.

---

## 12. Redis

Production uses:

```text
Redis 8 Alpine
```

Redis is password-protected.

The production configuration enables persistence and supplies authentication through deployment environment configuration.

Redis is reachable by FastAPI through the private Docker data network.

The Redis port is not host-published.

---

## 13. Docker Networks

Production defines separate network boundaries.

### Web network

Used for:

```text
nginx
frontend
backend
```

### Data network

Used for:

```text
backend
postgres
redis
migration service
identity-bootstrap service
```

The data network is configured as:

```text
internal: true
```

This reduces external network exposure for database infrastructure.

---

## 14. Database Migration Gate

Database schema migration is performed by a dedicated one-shot deployment service.

The migration command is:

```text
alembic upgrade head
```

FastAPI does not independently attempt to migrate its database when every application process starts.

The intended deployment chain is:

```text
PostgreSQL healthy
       |
       v
Alembic migration succeeds
       |
       v
Identity bootstrap succeeds
       |
       v
FastAPI starts
```

The current migration history contains:

```text
7 revisions
1 branch
1 head
```

Current head:

```text
17f167659ec9
```

---

## 15. Identity Bootstrap Gate

After successful migration, deployment runs:

```text
python -m scripts.seed_identity --skip-admin
```

This synchronizes:

```text
17 permissions
super_admin
admin
editor
viewer
```

The bootstrap does not automatically create a production administrator in normal Compose startup.

That is deliberate.

Administrative credentials must not be embedded in:

```text
Dockerfiles
docker-compose.production.yml
tracked environment files
GitHub Actions workflows
```

---

## 16. Production Content Seeding

Portfolio development content is not automatically executed during production startup.

The existence of:

```text
backend/scripts/seed_portfolio.py
```

does not make portfolio data part of deployment infrastructure.

Production content should be added through:

```text
the protected administration interface
approved API operations
an explicitly reviewed one-time content operation
```

This prevents infrastructure startup from silently publishing development or placeholder portfolio data.

---

## 17. Health Checks

The production stack has separate health boundaries.

### Nginx

```text
GET /healthz
```

Expected:

```text
200
healthy
```

### Next.js

```text
GET /api/health
```

Expected service identity:

```text
portfolio-web
```

### FastAPI liveness

```text
GET /api/v1/health/live
```

Confirms the backend process is alive.

### FastAPI readiness

```text
GET /api/v1/health/ready
```

Confirms dependencies including:

```text
PostgreSQL
Redis
```

are healthy.

This separation permits orchestration to distinguish:

```text
process running
```

from:

```text
service ready for application traffic
```

---

## 18. Validated Production Stack State

A clean production-stack smoke test successfully created and validated:

```text
postgres
redis
migrate
identity-bootstrap
backend
frontend
nginx
```

Expected steady-state service statuses are:

```text
postgres             Up / healthy
redis                Up / healthy
migrate              Exited (0)
identity-bootstrap   Exited (0)
backend              Up / healthy
frontend             Up / healthy
nginx                Up / healthy
```

`migrate` and `identity-bootstrap` are intentionally one-shot services.

Their successful state is:

```text
Exited (0)
```

rather than continuously running.

---

## 19. Reverse-Proxy Security Headers

The Nginx boundary has been validated to return:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

These headers provide baseline browser-side hardening.

HTTPS-specific controls such as final HSTS policy should be reviewed only after the real TLS/public-domain architecture is established.

---

## 20. Non-Root Runtime Validation

Application containers have been verified to run as non-root users.

Backend:

```text
appuser
```

Frontend:

```text
nextjs
```

This reduces the privileges available to application processes if they are compromised.

---

## 21. Secret Management

The following file contains actual local production-stack secrets:

```text
infrastructure/production.env
```

It is intentionally excluded from Git.

The tracked template is:

```text
infrastructure/production.env.example
```

The real file must never be:

```text
committed
staged
copied into Docker build context
printed in CI logs
embedded into container images
```

Dockerfile-specific ignore files also exclude the real production environment file from build contexts.

---

## 22. Critical Production Secrets

At minimum, independently generated production secrets include:

```text
POSTGRES_PASSWORD
REDIS_PASSWORD
JWT_SECRET_KEY
CONTACT_HASH_SECRET_KEY
```

These values must differ from:

```text
development credentials
test credentials
CI credentials
historical rotated values
```

`JWT_SECRET_KEY` and `CONTACT_HASH_SECRET_KEY` must not intentionally reuse one another.

---

## 23. Frontend Public vs Private Configuration

Variables prefixed with:

```text
NEXT_PUBLIC_
```

may be compiled into browser-accessible JavaScript.

They must therefore never contain secrets.

The internal server-to-server backend address is configured separately through:

```text
BACKEND_API_URL
```

Example production Docker value:

```text
http://backend:8000/api/v1
```

This value is used by Next.js server-side code and the BFF.

---

## 24. CI Readiness

The repository contains independent GitHub Actions workflows:

```text
.github/workflows/backend-ci.yml
.github/workflows/frontend-ci.yml
```

Both have been remotely validated.

### Backend CI

Validates:

```text
locked dependency installation
Ruff
mypy
single Alembic head
fresh PostgreSQL migration
full pytest suite
```

PostgreSQL 17 is provisioned as a CI service.

### Frontend CI

Validates:

```text
frozen pnpm installation
approved dependency build scripts
ESLint
TypeScript
Next.js production build
standalone output
```

The frontend CI job intentionally does not start FastAPI.

---

## 25. Supply-Chain Build Policy

pnpm native/install-time dependency scripts are explicitly allowlisted.

The current approved builds are:

```text
sharp@0.34.5
unrs-resolver@1.12.2
```

Global unrestricted dependency build-script execution is not enabled.

Future packages that require installation scripts should be deliberately reviewed before being added to the allowlist.

---

## 26. Validated Application Routes

Production smoke validation has confirmed successful responses through Nginx for:

```text
/
/about
/projects
/experience
/contact
/admin/login
```

The route checks demonstrate that:

```text
Nginx
Next.js
FastAPI routing
```

can coexist correctly in the production stack.

---

## 27. Remaining Public-Launch Requirements

The container architecture is production-oriented, but the following operational items remain before a final public launch.

### Hosting

A target production host/provider must be selected and provisioned.

### Domain

Production DNS records must point to the selected deployment boundary.

### TLS

The public site must be served through HTTPS.

The current local production smoke stack uses HTTP and does not represent the final TLS configuration.

### Backup and recovery

A real PostgreSQL backup policy must be configured and tested.

A backup is not considered operationally complete until restoration has been tested.

### Monitoring

At minimum, production monitoring should cover:

```text
public availability
Nginx health
Next.js health
FastAPI readiness
database availability
Redis availability
application errors
container restart loops
disk capacity
backup failures
```

### Logs

A production log-retention approach should be selected.

### Administrator initialization

The first real administrator should be created through an explicit controlled process after the production identity foundation is ready.

---

## 28. Production Readiness Decision

Current status:

```text
Application functionality             READY
Production-safe configuration         READY
Container images                      READY
Container networking                  READY
Fresh database migrations             READY
Identity bootstrap                    READY
Health checks                         READY
Security headers                      READY
Non-root app containers               READY
Frontend backend-independent build    READY
Backend CI                            READY
Frontend CI                           READY

Hosting provider                      PENDING
Public DNS                            PENDING
HTTPS/TLS                             PENDING
Backups/restore                       PENDING
Monitoring/alerting                   PENDING
Final production deployment           PENDING
```

The system is therefore considered:

```text
APPLICATION + CONTAINER DEPLOYMENT READY
```

but not yet:

```text
PUBLIC PRODUCTION LAUNCH COMPLETE
```

---

## 29. Release Principle

A production deployment should be performed only from an explicitly approved Git commit or release tag.

Do not deploy an unreviewed moving development workspace.

The release candidate should have:

```text
clean Git working tree
successful backend CI
successful frontend CI
reviewed deployment environment
reviewed migration head
reviewed infrastructure diff
```

---

## 30. Related Documentation

See:

```text
docs/deployment/environment-variables.md
docs/deployment/production-runbook.md
docs/database/migrations.md
docs/security/authentication.md
docs/security/authorization.md
docs/architecture/system-overview.md
```
