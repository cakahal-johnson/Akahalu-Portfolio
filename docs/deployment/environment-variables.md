# Akahalu Portfolio — Environment Variables

## 1. Purpose

Akahalu Portfolio separates configuration from source code.

Environment configuration is divided between:

```text
backend development
frontend development
production container infrastructure
```

The tracked templates are:

```text
backend/.env.example
frontend/.env.example
infrastructure/production.env.example
```

The corresponding real environment files may contain secrets and must not be committed.

---

## 2. Configuration Files

### Backend local development

Real file:

```text
backend/.env
```

Template:

```text
backend/.env.example
```

### Frontend local development

Typical real file:

```text
frontend/.env.local
```

Template:

```text
frontend/.env.example
```

### Production Compose

Real file:

```text
infrastructure/production.env
```

Template:

```text
infrastructure/production.env.example
```

The real production file is Git-ignored.

---

## 3. Secret Classification

Variables should be treated as either:

```text
secret
private operational configuration
public/browser-safe configuration
```

### Secret values

Examples:

```text
POSTGRES_PASSWORD
REDIS_PASSWORD
JWT_SECRET_KEY
CONTACT_HASH_SECRET_KEY
```

### Private operational configuration

Examples:

```text
DATABASE_URL
REDIS_URL
BACKEND_API_URL
TRUSTED_HOSTS
DATABASE_POOL_SIZE
```

These values are not necessarily credentials themselves, but some contain credentials or internal infrastructure information and should remain server-side.

### Browser-safe configuration

Only values intentionally prefixed with:

```text
NEXT_PUBLIC_
```

should be considered browser-visible.

No secret may be placed in a `NEXT_PUBLIC_*` variable.

---

# 4. Compose Variables

## `COMPOSE_PROJECT_NAME`

Purpose:

```text
Controls the Docker Compose project namespace.
```

Example:

```text
akahalu-portfolio
```

Used to namespace:

```text
containers
networks
volumes
```

For destructive smoke testing, using a unique project name can avoid colliding with persistent production-like local volumes.

---

## `IMAGE_TAG`

Purpose:

```text
Controls the application Docker image tag.
```

Example:

```text
local
```

Production should preferably use an immutable release identifier such as:

```text
Git commit SHA
release version
build number
```

rather than relying indefinitely on a mutable `latest` tag.

---

## `BIND_ADDRESS`

Purpose:

```text
Controls which host address publishes the Nginx container.
```

Local smoke-test default:

```text
127.0.0.1
```

This intentionally limits the stack to the local host.

Changing it to a publicly reachable address is an infrastructure decision and must be accompanied by appropriate:

```text
TLS
firewall rules
host hardening
DNS
monitoring
```

---

## `HTTP_PORT`

Purpose:

```text
Host-side HTTP port mapped to Nginx port 80.
```

Local smoke-test example:

```text
8080
```

Production routing may use a different edge architecture.

---

# 5. PostgreSQL Variables

## `POSTGRES_DB`

Purpose:

```text
PostgreSQL database name.
```

Example:

```text
portfolio_db
```

---

## `POSTGRES_USER`

Purpose:

```text
PostgreSQL application/database owner username.
```

Example:

```text
portfolio_user
```

---

## `POSTGRES_PASSWORD`

Classification:

```text
SECRET
```

Purpose:

```text
Password for the PostgreSQL application user.
```

Requirements:

```text
high entropy
production-specific
not committed
not shared with development
```

Prefer URL-safe random values when they will also be embedded inside a PostgreSQL connection URL.

---

## `DATABASE_URL`

Classification:

```text
SECRET / PRIVATE
```

Production Docker format:

```text
postgresql+psycopg://<user>:<password>@postgres:5432/<database>
```

Example structure:

```text
postgresql+psycopg://portfolio_user:<password>@postgres:5432/portfolio_db
```

The hostname:

```text
postgres
```

is the Docker Compose service name.

The password embedded in this URL must match:

```text
POSTGRES_PASSWORD
```

when using the default production Compose setup.

---

## `DATABASE_ECHO`

Purpose:

```text
Controls SQLAlchemy SQL logging.
```

Production recommendation:

```text
false
```

Enabling verbose SQL output in production can create unnecessary log volume and may expose sensitive application context.

---

## `DATABASE_POOL_SIZE`

Purpose:

```text
Base SQLAlchemy database connection-pool size.
```

Current template:

```text
10
```

This value should eventually be tuned according to:

```text
application concurrency
PostgreSQL connection limit
number of backend instances
hosting resources
```

---

## `DATABASE_MAX_OVERFLOW`

Purpose:

```text
Maximum temporary connections above the normal pool size.
```

Current template:

```text
20
```

---

## `DATABASE_POOL_TIMEOUT`

Purpose:

```text
Number of seconds SQLAlchemy waits for a pool connection before timing out.
```

Current template:

```text
30
```

---

# 6. Redis Variables

## `REDIS_PASSWORD`

Classification:

```text
SECRET
```

Purpose:

```text
Password required by the production Redis service.
```

The production Compose service starts Redis with password authentication enabled.

---

## `REDIS_URL`

Classification:

```text
SECRET / PRIVATE
```

Production Docker format:

```text
redis://:<password>@redis:6379/0
```

Example structure:

```text
redis://:<password>@redis:6379/0
```

The password must match:

```text
REDIS_PASSWORD
```

when using the supplied Compose configuration.

The hostname:

```text
redis
```

is the internal Docker Compose service name.

---

# 7. Backend General Variables

## `APP_NAME`

Purpose:

```text
Application/service display name.
```

Example:

```text
Akahalu Portfolio API
```

---

## `APP_VERSION`

Purpose:

```text
Application version metadata.
```

Example:

```text
1.0.0
```

The value should eventually be aligned with the release-versioning policy.

---

## `ENVIRONMENT`

Allowed values:

```text
local
test
staging
production
```

Production must use:

```text
production
```

Several security behaviors depend on this setting.

---

## `DEBUG`

Production requirement:

```text
false
```

The backend rejects:

```text
DEBUG=true
```

when `ENVIRONMENT=production`.

---

## `API_V1_PREFIX`

Purpose:

```text
Versioned FastAPI base path.
```

Current value:

```text
/api/v1
```

Changing this affects:

```text
Nginx routing
frontend API URLs
BFF server configuration
documentation
tests
```

and should therefore be treated as an API architecture change.

---

## `API_DOCS_ENABLED`

Purpose:

```text
Controls FastAPI Swagger/OpenAPI web exposure.
```

Production recommendation:

```text
false
```

If omitted, production defaults to documentation disabled.

Validated production behavior:

```text
/docs         -> 404
/openapi.json -> 404
```

---

## `BACKEND_HOST`

Container value:

```text
0.0.0.0
```

This controls the FastAPI process listener inside the container.

It does not mean the backend is automatically public.

Public exposure is controlled by Docker port publishing and the Nginx boundary.

---

## `BACKEND_PORT`

Current internal port:

```text
8000
```

---

# 8. CORS Variables

## `ALLOWED_ORIGINS`

Purpose:

```text
Defines browser origins allowed by FastAPI CORS middleware.
```

The environment value must parse as a list.

Production example:

```text
["https://portfolio.example.com"]
```

If both apex and `www` sites legitimately make browser-origin requests, configure them explicitly as required.

Production validation rejects:

```text
[]
["*"]
["http://localhost:3000"]
["http://127.0.0.1:3000"]
```

as production origin configuration.

---

# 9. Trusted Hosts

## `TRUSTED_HOSTS`

Purpose:

```text
Defines hosts accepted by TrustedHostMiddleware.
```

Production Docker example:

```text
[
  "portfolio.example.com",
  "www.portfolio.example.com",
  "localhost",
  "127.0.0.1",
  "backend"
]
```

Why the internal names exist:

```text
backend
    -> internal Next.js-to-FastAPI traffic

127.0.0.1 / localhost
    -> container-local health and controlled local operations

public domains
    -> Nginx-proxied production traffic
```

Production rejects wildcard:

```text
*
```

---

# 10. JWT Variables

## `JWT_SECRET_KEY`

Classification:

```text
CRITICAL SECRET
```

Purpose:

```text
Signs and verifies access JWTs.
```

Requirements:

```text
high entropy
environment-specific
not committed
not logged
not browser-exposed
```

Rotating this value invalidates existing signed access JWTs.

Because authentication also uses server-side sessions, operational JWT-secret rotation should still be handled deliberately rather than casually changing the value during normal application operation.

---

## `JWT_ALGORITHM`

Current allowed value:

```text
HS256
```

The application configuration currently constrains the algorithm to HS256.

A future algorithm migration would require coordinated application/security changes and should not be performed by environment-variable substitution alone.

---

## `JWT_ISSUER`

Current default:

```text
akahalu-portfolio-api
```

Issued access tokens include this issuer and validation requires it.

---

## `JWT_AUDIENCE`

Current default:

```text
akahalu-portfolio-web
```

Issued access tokens include this audience and validation requires it.

---

# 11. Contact Security Variables

## `CONTACT_HASH_SECRET_KEY`

Classification:

```text
CRITICAL SECRET
```

Purpose:

```text
Provides keyed hashing material for privacy-preserving contact-submission security metadata.
```

This value must be different from:

```text
JWT_SECRET_KEY
```

It should have independent entropy and rotation planning.

---

## `CONTACT_DUPLICATE_WINDOW_MINUTES`

Purpose:

```text
Controls the configured duplicate-submission detection window.
```

Current default:

```text
15
```

Allowed configured range:

```text
1 through 1440 minutes
```

---

## `CONTACT_USER_AGENT_MAX_LENGTH`

Purpose:

```text
Limits retained contact-request user-agent length.
```

Current default:

```text
500
```

Allowed configuration range:

```text
100 through 512
```

---

# 12. Authentication Lifetime Variables

## `ACCESS_TOKEN_EXPIRE_MINUTES`

Default:

```text
15
```

Controls the short-lived access JWT lifetime.

---

## `REFRESH_TOKEN_EXPIRE_DAYS`

Default:

```text
30
```

Controls refresh-token and authentication-session renewal horizon.

---

## `EMAIL_VERIFICATION_EXPIRE_HOURS`

Default:

```text
24
```

Controls email-verification token expiry.

---

## `PASSWORD_RESET_EXPIRE_MINUTES`

Default:

```text
60
```

Controls password-reset token expiry.

---

## `MAXIMUM_FAILED_LOGIN_ATTEMPTS`

Default:

```text
5
```

Controls the number of consecutive invalid-password attempts before temporary lockout.

---

## `ACCOUNT_LOCKOUT_MINUTES`

Default:

```text
15
```

Controls temporary account-lock duration.

---

# 13. Frontend Public Variables

## `NEXT_PUBLIC_APP_URL`

Classification:

```text
PUBLIC
```

Purpose:

```text
Canonical public web application URL.
```

Local development example:

```text
http://localhost:3000
```

Local production-stack smoke example:

```text
http://localhost:8080
```

Real production example:

```text
https://portfolio.example.com
```

This value is browser-visible and must contain no secrets.

---

## `NEXT_PUBLIC_API_URL`

Classification:

```text
PUBLIC
```

Purpose:

```text
Public browser-visible FastAPI base URL.
```

Local development:

```text
http://127.0.0.1:8000/api/v1
```

Local production-stack smoke:

```text
http://localhost:8080/api/v1
```

Same-domain production:

```text
https://portfolio.example.com/api/v1
```

This value contains no credentials.

---

## `NEXT_PUBLIC_API_TIMEOUT_MS`

Classification:

```text
PUBLIC
```

Current value:

```text
15000
```

The timeout should not be increased merely to hide backend performance defects.

Application latency problems should be diagnosed at the source.

---

# 14. Frontend Server-Only Variable

## `BACKEND_API_URL`

Classification:

```text
PRIVATE SERVER CONFIGURATION
```

Purpose:

```text
Internal Next.js-to-FastAPI API base URL.
```

Local development example:

```text
http://127.0.0.1:8000/api/v1
```

Production Docker value:

```text
http://backend:8000/api/v1
```

This variable must remain server-only.

It must not be renamed to:

```text
NEXT_PUBLIC_BACKEND_API_URL
```

because the internal backend address is not intended for browser exposure.

---

# 15. Production URL Model

In a same-domain production deployment:

```text
Browser:
https://portfolio.example.com

Browser API:
https://portfolio.example.com/api/v1

Next.js BFF internal FastAPI:
http://backend:8000/api/v1
```

This separation is fundamental to the architecture.

---

# 16. Generating Secrets

Generate production secrets with a cryptographically secure random source.

One example using Python is:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Generate separate values for:

```text
POSTGRES_PASSWORD
REDIS_PASSWORD
JWT_SECRET_KEY
CONTACT_HASH_SECRET_KEY
```

Do not intentionally reuse one generated value across these settings.

For connection-string passwords, URL-safe random strings reduce escaping problems.

---

# 17. Creating the Production Environment File

Start from:

```text
infrastructure/production.env.example
```

Create:

```text
infrastructure/production.env
```

and replace every placeholder.

Never use a search-and-replace method that accidentally leaves malformed lines or duplicates keys.

After creation, validate:

```powershell
docker compose `
    --env-file .\infrastructure\production.env `
    -f .\docker-compose.production.yml `
    config --quiet
```

No output indicates successful Compose parsing.

---

# 18. Verify Production Environment Is Ignored

Run:

```powershell
git check-ignore -v `
    .\infrastructure\production.env
```

A matching `.gitignore` rule should be shown.

Then:

```powershell
git ls-files `
    .\infrastructure\production.env
```

Expected:

```text
no output
```

If the second command prints the production environment file, stop and remove it from Git tracking before continuing.

---

# 19. Docker Build-Context Protection

The production environment file is additionally excluded by:

```text
infrastructure/docker/backend.Dockerfile.dockerignore
infrastructure/docker/frontend.Dockerfile.dockerignore
```

This is important because:

```text
.gitignore
```

does not automatically remove files from a Docker build context.

Both protections should remain.

---

# 20. CI Environment Variables

CI uses isolated test-only values.

CI credentials must not be copied into real production deployment.

Likewise, production values must not be added to workflow YAML merely because a CI job requires configuration.

Use:

```text
test-only static values
GitHub secrets when an actual secret integration is required
```

according to the CI purpose.

---

# 21. Rotation Guidance

### JWT secret

Rotation invalidates existing JWT signatures.

Perform during a controlled authentication/session maintenance event.

### PostgreSQL password

Requires coordinated update of:

```text
database account password
POSTGRES_PASSWORD
DATABASE_URL
```

### Redis password

Requires coordinated update of:

```text
Redis password
REDIS_PASSWORD
REDIS_URL
```

### Contact hash secret

Rotation may change future keyed hashes/fingerprints relative to historical records.

Plan rotation according to the intended duplicate/security-data semantics.

---

# 22. Never Commit

The following must never be committed with real values:

```text
backend/.env
frontend/.env.local
infrastructure/production.env
private keys
TLS private keys
database exports
backup archives containing private data
credential files
```

Tracked `.example` files must contain placeholders only.

---

# 23. Validation Checklist

Before production deployment confirm:

```text
ENVIRONMENT=production
DEBUG=false
API_DOCS_ENABLED=false

ALLOWED_ORIGINS contains real HTTPS domain(s)
TRUSTED_HOSTS contains real domain(s) and required internal hosts

POSTGRES_PASSWORD replaced
DATABASE_URL contains matching production password

REDIS_PASSWORD replaced
REDIS_URL contains matching production password

JWT_SECRET_KEY replaced
CONTACT_HASH_SECRET_KEY replaced and differs from JWT secret

NEXT_PUBLIC_APP_URL uses final public HTTPS URL
NEXT_PUBLIC_API_URL uses final public API URL
BACKEND_API_URL uses internal Docker backend service
```

---

# 24. Related Documentation

See:

```text
docs/deployment/deployment-readiness.md
docs/deployment/production-runbook.md
docs/security/authentication.md
docs/architecture/frontend-architecture.md
docs/architecture/system-overview.md
```
