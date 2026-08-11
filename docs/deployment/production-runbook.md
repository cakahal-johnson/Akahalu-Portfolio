# Akahalu Portfolio — Production Runbook

## 1. Purpose

This runbook describes the controlled deployment and operational validation procedure for the Akahalu Portfolio production container stack.

The current infrastructure is based on:

```text
Docker Compose
Nginx
Next.js
FastAPI
PostgreSQL
Redis
Alembic
identity bootstrap
```

The procedure should be adapted to the selected production hosting platform while preserving the documented security and startup boundaries.

---

## 2. Production Principles

A production deployment must preserve these rules:

```text
Deploy an approved Git revision.
Never commit production secrets.
Do not expose PostgreSQL directly.
Do not expose Redis directly.
Do not expose FastAPI directly when Nginx is the intended edge.
Run migrations before normal backend traffic.
Run identity synchronization after migrations.
Do not automatically seed portfolio content.
Run application containers as non-root users.
Serve the public production deployment over HTTPS.
Do not destroy persistent volumes during routine deployment.
```

---

# 3. Required Files

Production deployment depends on:

```text
docker-compose.production.yml

infrastructure/production.env

infrastructure/docker/backend.Dockerfile
infrastructure/docker/backend.Dockerfile.dockerignore

infrastructure/docker/frontend.Dockerfile
infrastructure/docker/frontend.Dockerfile.dockerignore

infrastructure/nginx/portfolio.conf

infrastructure/postgres/init.sql
```

The real:

```text
infrastructure/production.env
```

must exist on the deployment host but remain outside Git.

---

# 4. Pre-Deployment Git Check

Deploy an explicitly approved release commit.

Run:

```powershell
git status
```

The release workspace should not contain unintended local application modifications.

Review:

```powershell
git log --oneline -10
```

Record the exact deployment commit.

For formal releases, prefer an immutable:

```text
Git commit SHA
release tag
```

over a moving branch reference.

---

# 5. CI Gate

Before production deployment, the release revision should have successful:

```text
Backend CI
Frontend CI
```

Backend CI must verify:

```text
Ruff
mypy
single Alembic head
fresh migration
pytest
```

Frontend CI must verify:

```text
frozen pnpm install
lint
TypeScript
production build
standalone output
```

A failing required workflow is a release blocker until the failure is understood and resolved.

---

# 6. Production Environment Preparation

Copy:

```text
infrastructure/production.env.example
```

to:

```text
infrastructure/production.env
```

Do not overwrite an existing production environment file without reviewing its current values.

Generate independent high-entropy values for:

```text
POSTGRES_PASSWORD
REDIS_PASSWORD
JWT_SECRET_KEY
CONTACT_HASH_SECRET_KEY
```

One suitable local generation command is:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run it separately for each secret.

---

# 7. Configure Production Domains

Update:

```text
ALLOWED_ORIGINS
TRUSTED_HOSTS
NEXT_PUBLIC_APP_URL
NEXT_PUBLIC_API_URL
```

for the real production domain.

Example architecture:

```text
NEXT_PUBLIC_APP_URL=https://portfolio.example.com

NEXT_PUBLIC_API_URL=https://portfolio.example.com/api/v1

BACKEND_API_URL=http://backend:8000/api/v1

ALLOWED_ORIGINS=["https://portfolio.example.com"]

TRUSTED_HOSTS=[
  "portfolio.example.com",
  "www.portfolio.example.com",
  "localhost",
  "127.0.0.1",
  "backend"
]
```

Use only domains actually intended for the deployment.

---

# 8. Verify Secret File Protection

Before deployment:

```powershell
git check-ignore -v `
    .\infrastructure\production.env
```

The file should be ignored.

Then:

```powershell
git ls-files `
    .\infrastructure\production.env
```

Expected:

```text
no output
```

Do not continue if the real production environment file is tracked.

---

# 9. Validate Compose Configuration

From the repository root:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    config --quiet
```

Expected:

```text
no output
```

Any interpolation, syntax, or required-variable error must be fixed before containers are started.

---

# 10. Review Rendered Compose Safely

When necessary, inspect structural configuration using:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    config
```

Be aware that rendered Compose output may include sensitive environment values.

Do not:

```text
paste it into public issue trackers
commit it to the repository
save it into CI artifacts
share it in logs without redaction
```

Use `config --quiet` for normal syntax validation.

---

# 11. Build Production Images

Build:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    build `
    --pull
```

The backend build should:

```text
install locked production Python dependencies
copy application/migration/script source
create non-root runtime
```

The frontend build should:

```text
install frozen pnpm dependencies
execute approved native build scripts
build Next.js
produce standalone output
create non-root runtime
```

---

# 12. Image Tagging

The Compose configuration supports:

```text
IMAGE_TAG
```

For real production releases, use an immutable release identifier where practical.

Example:

```text
IMAGE_TAG=<git-sha>
```

This makes application rollback and deployment auditing more reliable than a permanently mutable image tag.

---

# 13. Start the Stack

Run:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    up -d
```

The expected dependency sequence is:

```text
PostgreSQL
    |
    v
migrate
    |
    v
identity-bootstrap
    |
    v
backend
    |
    v
frontend
    |
    v
nginx
```

Redis also becomes healthy before the backend is considered ready.

---

# 14. Inspect All Services

Run:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    ps -a
```

Expected steady-state pattern:

```text
postgres             Up / healthy
redis                Up / healthy
migrate              Exited (0)
identity-bootstrap   Exited (0)
backend              Up / healthy
frontend             Up / healthy
nginx                Up / healthy
```

Do not interpret successful one-shot services as failures merely because they are no longer running.

For:

```text
migrate
identity-bootstrap
```

the desired result is:

```text
Exited (0)
```

---

# 15. Inspect Migration Logs

Run:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs migrate
```

Verify:

```text
Alembic connected successfully
migration chain completed
no traceback
exit code 0
```

The current expected head is:

```text
17f167659ec9
```

---

# 16. Inspect Identity Bootstrap

Run:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs identity-bootstrap
```

Expected synchronized identity state:

```text
17 permissions
super_admin
admin
editor
viewer
```

Any failure here should be treated as an authorization deployment failure.

Do not allow a new application version that requires new permission codes to serve normally while identity synchronization remains incomplete.

---

# 17. Verify Nginx

Run:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    exec nginx `
    nginx -t
```

Expected:

```text
syntax is ok
test is successful
```

---

# 18. Verify Non-Root Application Containers

Get container IDs:

```powershell
$backendContainer = docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    ps -q backend

$frontendContainer = docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    ps -q frontend
```

Inspect runtime users:

```powershell
docker inspect `
    --format '{{.Config.User}}' `
    $backendContainer

docker inspect `
    --format '{{.Config.User}}' `
    $frontendContainer
```

Expected:

```text
appuser
nextjs
```

---

# 19. Verify Service Exposure

Run:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    ps
```

The host should not publish:

```text
postgres:5432
redis:6379
backend:8000
frontend:3000
```

Only the intended Nginx edge should have a host mapping.

Local smoke configuration:

```text
127.0.0.1:8080 -> 80/tcp
```

Public production exposure will depend on the selected host/TLS architecture.

---

# 20. Verify Nginx Health

For the local production-stack smoke configuration:

```powershell
Invoke-WebRequest `
    http://localhost:8080/healthz `
    -UseBasicParsing
```

Expected HTTP status:

```text
200
```

Expected body:

```text
healthy
```

Adapt the URL to the final HTTPS production domain after public deployment.

---

# 21. Verify Next.js Health

Local smoke:

```powershell
Invoke-RestMethod `
    http://localhost:8080/api/health
```

Expected response includes:

```text
status  = healthy
service = portfolio-web
```

---

# 22. Verify FastAPI Liveness

Local smoke:

```powershell
Invoke-RestMethod `
    http://localhost:8080/api/v1/health/live
```

Expected:

```text
healthy
portfolio-api
production
```

---

# 23. Verify FastAPI Readiness

Run:

```powershell
Invoke-RestMethod `
    http://localhost:8080/api/v1/health/ready
```

Expected readiness includes healthy:

```text
database
redis
```

If liveness succeeds but readiness fails:

```text
do not assume the backend is safe for normal production traffic
```

Inspect dependency logs and health state first.

---

# 24. Verify API Documentation Is Disabled

Inside the backend container:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    exec backend `
    python -c "import urllib.request,urllib.error; u='http://127.0.0.1:8000/docs'; exec('try:\n r=urllib.request.urlopen(u); print(r.status)\nexcept urllib.error.HTTPError as e:\n print(e.code)')"
```

Expected:

```text
404
```

Then:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    exec backend `
    python -c "import urllib.request,urllib.error; u='http://127.0.0.1:8000/openapi.json'; exec('try:\n r=urllib.request.urlopen(u); print(r.status)\nexcept urllib.error.HTTPError as e:\n print(e.code)')"
```

Expected:

```text
404
```

---

# 25. Verify Security Headers

Run:

```powershell
$response = Invoke-WebRequest `
    http://localhost:8080/ `
    -UseBasicParsing

"X-Content-Type-Options: $($response.Headers['X-Content-Type-Options'])"
"X-Frame-Options: $($response.Headers['X-Frame-Options'])"
"Referrer-Policy: $($response.Headers['Referrer-Policy'])"
"Permissions-Policy: $($response.Headers['Permissions-Policy'])"
```

Expected:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

For the public production deployment, perform the same check against the final HTTPS domain.

---

# 26. Public Route Smoke Test

Test:

```powershell
$urls = @(
    "http://localhost:8080/",
    "http://localhost:8080/about",
    "http://localhost:8080/projects",
    "http://localhost:8080/experience",
    "http://localhost:8080/contact",
    "http://localhost:8080/admin/login"
)

foreach ($url in $urls) {
    try {
        $result = Invoke-WebRequest `
            $url `
            -UseBasicParsing

        "$url -> $($result.StatusCode)"
    }
    catch {
        "$url -> FAILED"
    }
}
```

Expected:

```text
all routes -> 200
```

Replace the base URL with the public HTTPS URL during final launch verification.

---

# 27. Initial Production Administrator

Normal production startup uses:

```text
python -m scripts.seed_identity --skip-admin
```

and therefore does not automatically create an administrator.

For the first production administrator, use the repository's explicit identity setup procedure rather than placing credentials in Compose.

One controlled method is to run the identity script manually without `--skip-admin`:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    run --rm backend `
    python -m scripts.seed_identity
```

Follow the script's administrator creation/recovery prompts.

Do this only through a trusted deployment terminal.

Do not paste the resulting credentials into:

```text
Git commits
issue trackers
deployment documentation
shared logs
```

After creation, test `/admin/login` normally.

---

# 28. Verify Administrator Authentication

After the production administrator exists:

1. open the final `/admin/login`;
2. sign in;
3. confirm the dashboard loads;
4. verify the expected administration modules;
5. confirm role/permission restrictions;
6. confirm logout removes the session;
7. confirm protected routes require authentication afterward.

Do not use an administrator account for public application operations where authentication is unnecessary.

---

# 29. Production Data

Do not automatically run:

```text
seed_portfolio.py
```

unless that exact content has been reviewed and explicitly approved for production.

Preferred production content workflow:

```text
administrator login
       |
       v
protected administration UI
       |
       v
reviewed content creation
       |
       v
public visibility enabled explicitly
```

---

# 30. Logs

Inspect application logs when a health check or smoke test fails.

### Nginx

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs --tail 200 nginx
```

### Frontend

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs --tail 200 frontend
```

### Backend

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs --tail 200 backend
```

### PostgreSQL

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs --tail 200 postgres
```

### Redis

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs --tail 200 redis
```

Do not publicly share logs without reviewing them for sensitive information.

---

# 31. Restarting Application Services

A routine service restart can be performed without deleting persistent volumes.

Example:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    restart backend frontend nginx
```

After restart, repeat health validation.

---

# 32. Stopping the Stack

To stop and remove containers/networks while retaining named volumes:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    down
```

This should not remove named persistent volumes.

---

# 33. Do Not Use `down -v` Casually

Avoid:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    down -v
```

The `-v` option removes named volumes associated with the Compose project.

That may destroy:

```text
PostgreSQL data
Redis persistence
Next.js cache data
```

On a production deployment, deleting the PostgreSQL volume can destroy the application database.

Use volume-destructive commands only when deliberately resetting an environment and after confirming backups.

---

# 34. Database Backup Requirement

Before the public production launch, establish a real PostgreSQL backup strategy.

Preferred options depend on the selected hosting architecture and can include:

```text
managed database automated backups
provider snapshots
scheduled pg_dump backups
point-in-time recovery
```

At minimum, define:

```text
backup frequency
retention period
encrypted storage location
access-control policy
restoration procedure
restoration test frequency
```

A backup strategy is not considered complete until a restore has been successfully tested.

---

# 35. Pre-Migration Backup

Before deploying a schema migration that can alter or remove existing production data:

```text
take/verify backup
verify migration in CI
review migration source
record current application/image version
record current database revision
apply migration
verify new database revision
verify backend readiness
verify public/application smoke tests
```

Do not assume that the presence of an Alembic `downgrade()` method eliminates the need for a backup.

---

# 36. Database Revision Check

Where operationally needed:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    exec backend `
    alembic current
```

Expected current revision at the time of this document:

```text
17f167659ec9 (head)
```

Future deployments should compare against the release's current migration head rather than permanently assuming this revision.

---

# 37. Deployment of a New Application Version

For a normal update:

```text
1. confirm CI success
2. record current release/image
3. verify backup state when schema changes are involved
4. fetch approved release revision
5. update IMAGE_TAG if used
6. validate Compose configuration
7. build/pull new images
8. run Compose deployment
9. allow migration + identity bootstrap gates to complete
10. verify service health
11. perform application smoke tests
12. monitor logs/errors
```

---

# 38. Rollback Principle

Application rollback and database rollback are different operations.

If a deployment fails after a backward-compatible migration, it may be possible to:

```text
restore previous application image
leave newer compatible schema in place
```

This is often safer than immediately downgrading the database.

Do not automatically execute:

```text
alembic downgrade
```

as the first response to an application failure.

A database downgrade can itself be destructive.

Review the migration and data compatibility first.

---

# 39. Immutable Image Rollback

When production images use immutable release tags, application rollback can select a previously known-good:

```text
IMAGE_TAG
```

and redeploy that release.

Record:

```text
previous tag
new tag
database revision
deployment time
```

for each production change.

This improves recovery compared with depending on an overwritten mutable image tag.

---

# 40. Secret Rotation

If a production secret may be compromised:

### JWT secret

Rotate:

```text
JWT_SECRET_KEY
```

and plan for existing access JWT invalidation.

Existing database sessions/refresh state should also be reviewed according to the incident.

### PostgreSQL

Rotate the database credential and update:

```text
POSTGRES_PASSWORD
DATABASE_URL
```

together.

### Redis

Rotate:

```text
REDIS_PASSWORD
REDIS_URL
```

together.

### Contact hash secret

Rotate:

```text
CONTACT_HASH_SECRET_KEY
```

with awareness that keyed hashes created before and after rotation may not be comparable.

After any rotation:

```text
restart affected services
validate health
validate authentication where relevant
review logs
```

---

# 41. Incident: Backend Unhealthy

If:

```text
/api/v1/health/live = healthy
```

but:

```text
/api/v1/health/ready = unhealthy
```

inspect:

```text
PostgreSQL health
Redis health
backend logs
database connection configuration
Redis authentication configuration
Docker network state
```

Do not route normal production traffic to a dependency-unready backend.

---

# 42. Incident: Frontend Unhealthy

Inspect:

```text
frontend container status
frontend logs
/api/health
container restart count
Next.js runtime files
environment configuration
```

Because the image build is backend-independent, a frontend container failing to start should be investigated independently from whether FastAPI happened to be available at build time.

---

# 43. Incident: Migration Failure

If `migrate` exits non-zero:

```text
do not bypass the migration service
do not manually start a newer backend against an unknown schema
```

Inspect:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs migrate
```

Verify:

```text
DATABASE_URL
PostgreSQL health
extension availability
current migration history
migration DDL/data requirements
```

Resolve the schema issue before allowing the new backend version to serve.

---

# 44. Incident: Identity Bootstrap Failure

If identity bootstrap fails:

```text
new non-superuser authorization requirements may not exist in the database
```

Inspect:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    logs identity-bootstrap
```

Do not work around the failure by removing FastAPI permission dependencies.

Fix the identity synchronization issue.

---

# 45. Incident: Refresh-Token Reuse

The backend treats refresh-token reuse as a security event.

When reuse is detected:

```text
token family revoked
authentication session revoked
refresh rejected
```

The affected user must authenticate again.

If unexpected reuse events appear repeatedly:

```text
review browser/tab behavior
review application logs
review credential exposure possibilities
review deployment instances
consider forced session revocation
```

Do not disable reuse detection to eliminate the symptom.

---

# 46. Final Public Launch Checklist

Before announcing the portfolio publicly, confirm:

```text
approved release deployed

HTTPS valid
DNS correct

Nginx healthy
Next.js healthy
FastAPI live
FastAPI ready
PostgreSQL healthy
Redis healthy

/docs returns 404
/openapi.json returns 404

security headers present

public routes return 200
admin login works

production administrator secured

public profile reviewed
projects reviewed
experience reviewed
contact form tested

backup configured
restore procedure documented/tested

monitoring enabled
log access available

production environment file untracked
no production secrets in Git
```

---

# 47. Post-Deployment Observation

Immediately after a release, review:

```text
container health
restart counts
Nginx errors
Next.js errors
FastAPI errors
database errors
Redis errors
authentication failures
contact-submission failures
```

A successful `docker compose up -d` is only the beginning of deployment verification.

---

# 48. Documentation Maintenance

Update this runbook whenever deployment architecture changes, including changes to:

```text
hosting provider
TLS termination
domain architecture
container topology
backup provider
database hosting
Redis hosting
monitoring
CI/CD
release tagging
migration process
secret management
```

Commands documented here should reflect the actual deployment architecture rather than historical assumptions.

---

# 49. Related Documentation

See:

```text
docs/deployment/deployment-readiness.md
docs/deployment/environment-variables.md
docs/database/migrations.md
docs/security/authentication.md
docs/security/authorization.md
docs/architecture/system-overview.md
```
