# Authentication

## 1. Purpose

This document describes the authentication architecture and security controls used by Akahalu Portfolio.

The platform separates authentication responsibilities across three layers:

1. the browser;
2. the Next.js application and Backend-for-Frontend (BFF);
3. the FastAPI authentication service.

FastAPI remains the authoritative identity and session service. The Next.js BFF provides a secure browser boundary for administrator authentication and prevents raw access and refresh tokens from being exposed directly to browser JavaScript.

Authentication is distinct from authorization:

* authentication establishes who the user is and whether the authentication session is valid;
* authorization determines what the authenticated user is allowed to do.

Authorization is documented separately in `docs/security/authorization.md`.

---

## 2. Authentication Architecture

The administrative authentication path is:

```text
Browser
   |
   | Same-origin request
   | HttpOnly authentication cookies
   v
Next.js BFF
   |
   | Authorization: Bearer <access token>
   | or server-side refresh request
   v
FastAPI
   |
   +---- access-token validation
   |
   +---- session validation
   |
   +---- user-state validation
   |
   v
PostgreSQL
```

The browser does not need direct access to the FastAPI bearer token.

For administrator requests:

```text
Browser
  -> Next.js /api/admin/*
  -> authenticated BFF proxy
  -> FastAPI /api/v1/admin/*
```

For administrator session management:

```text
Browser
  -> Next.js /api/admin-auth/*
  -> FastAPI /api/v1/auth/*
```

This architecture keeps bearer credentials on the server side of the browser boundary while retaining FastAPI as the source of truth for authentication.

---

## 3. Primary Backend Authentication Components

The main backend implementation is located in:

```text
backend/app/api/dependencies/authentication.py
backend/app/api/v1/endpoints/auth.py
backend/app/security/passwords.py
backend/app/security/tokens.py
backend/app/services/authentication_service.py
backend/app/repositories/session_repository.py
backend/app/repositories/refresh_token_repository.py
backend/app/repositories/login_attempt_repository.py
backend/app/models/session.py
backend/app/models/refresh_token.py
backend/app/models/login_attempt.py
backend/app/models/user.py
```

Account-lifecycle security is implemented through:

```text
backend/app/api/v1/endpoints/account_lifecycle.py
backend/app/security/account_tokens.py
backend/app/services/account_lifecycle_service.py
backend/app/repositories/email_verification_token_repository.py
backend/app/repositories/password_reset_token_repository.py
backend/app/models/email_verification_token.py
backend/app/models/password_reset_token.py
```

---

## 4. Authentication Endpoints

The FastAPI authentication router exposes the following operations beneath `/api/v1`:

```text
POST /auth/login
POST /auth/refresh
POST /auth/logout
POST /auth/logout-all
GET  /auth/me
```

Therefore the full production API paths are:

```text
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/logout-all
GET  /api/v1/auth/me
```

Account-lifecycle routes under `/api/v1/account` provide email-verification and password-recovery functionality.

The frontend administrator BFF exposes:

```text
POST /api/admin-auth/login
POST /api/admin-auth/logout
POST /api/admin-auth/refresh
GET  /api/admin-auth/session
```

These Next.js endpoints are the intended browser-facing authentication boundary for the administration interface.

---

## 5. Password Storage

Passwords are never stored as plaintext.

Password hashing is isolated in:

```text
backend/app/security/passwords.py
```

The backend uses `pwdlib` with Argon2 support for password hashing.

The backend dependency declaration includes:

```text
pwdlib[argon2]
```

Application services interact with password hashes through dedicated helpers rather than implementing password hashing directly.

The authentication service uses a verification operation that can also return an updated hash. This permits transparent password-hash upgrades when the configured hashing policy changes.

On a successful login, when the password library determines that a stored hash should be upgraded:

```text
user.password_hash
```

is replaced with the updated hash and:

```text
user.password_changed_at
```

is updated.

This allows password hashing parameters to evolve without requiring all users to reset their passwords simultaneously.

---

## 6. Login Flow

Authentication begins with:

```text
POST /api/v1/auth/login
```

The login service normalizes the supplied email address by trimming whitespace and converting it to lowercase before lookup.

The high-level login sequence is:

```text
credentials received
        |
        v
normalize email
        |
        v
find user
        |
        v
validate account state
        |
        v
validate account lockout
        |
        v
verify password
        |
        v
require verified account
        |
        v
reset login-failure state
        |
        v
create authentication session
        |
        v
create refresh-token family
        |
        v
issue access + refresh tokens
```

### Unknown users

If no account exists for the submitted email:

* the failed attempt is recorded;
* the failure reason is internally recorded as `unknown_user`;
* the external response remains a generic invalid-credentials response.

The caller receives an error equivalent to:

```text
The email address or password is incorrect.
```

The response does not reveal whether the email address exists.

### Disabled or deleted accounts

An account cannot log in if:

```text
is_active == false
```

or:

```text
deleted_at != null
```

Such attempts are recorded with the internal failure reason:

```text
account_disabled
```

and authentication is rejected.

### Email verification

The login service requires:

```text
is_verified == true
```

before issuing a new authentication session.

An otherwise valid but unverified account receives an `email_not_verified` authentication error.

The FastAPI `get_current_user` dependency itself primarily validates token, session, active state, and deletion state. Initial login enforces email verification, while the Next.js administrative eligibility check also requires the account to remain verified.

---

## 7. Login Attempt Recording

Authentication attempts are persisted using the login-attempt repository.

Recorded information can include:

```text
email
user_id
IP address
user agent
success/failure state
failure reason
timestamp
```

Examples of internal failure reasons include:

```text
unknown_user
invalid_password
account_locked
account_disabled
email_not_verified
```

Successful authentication attempts are recorded as successful.

This history supports security review and account-protection workflows without changing the external invalid-credentials response into an account-discovery mechanism.

---

## 8. Account Lockout

The default login-protection configuration is:

```text
MAXIMUM_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES       = 15
```

These values are environment-configurable.

For each invalid password:

```text
failed_login_attempts += 1
```

When the configured threshold is reached:

```text
locked_until = now + account_lockout_minutes
```

and the service returns an account-locked response.

While:

```text
locked_until > current time
```

subsequent login attempts are rejected with HTTP `423 Locked`.

After a successful login:

```text
failed_login_attempts = 0
locked_until = null
```

This prevents accumulated historical failures from permanently affecting a successfully authenticated account.

Password-reset logic also clears failed-login/lockout state as part of account recovery.

---

## 9. Access Tokens

Access tokens are JSON Web Tokens.

They are created by:

```text
backend/app/security/tokens.py
```

The current signing algorithm is constrained by configuration to:

```text
HS256
```

The signing secret is supplied through:

```text
JWT_SECRET_KEY
```

and must never be committed to source control.

### Access-token lifetime

The default lifetime is:

```text
15 minutes
```

through:

```text
ACCESS_TOKEN_EXPIRE_MINUTES
```

Short-lived access tokens limit the exposure window of an individual bearer credential.

### JWT claims

Issued access tokens include:

```text
sub
sid
jti
iat
nbf
exp
iss
aud
typ
```

Their meanings are:

```text
sub  = authenticated user ID
sid  = authentication session ID
jti  = unique access-token ID
iat  = issued-at time
nbf  = not-before time
exp  = expiry time
iss  = configured issuer
aud  = configured audience
typ  = "access"
```

The configured defaults are:

```text
issuer   = akahalu-portfolio-api
audience = akahalu-portfolio-web
```

### Validation

Access-token decoding validates the configured:

```text
signing secret
algorithm
issuer
audience
required token claims
expiry
```

Malformed, invalid, or expired tokens are rejected.

Possession of a cryptographically valid access token is not sufficient by itself to access protected resources. The token must also reference a currently valid server-side session.

---

## 10. Database-Backed Session Validation

Every protected FastAPI request using the standard authentication dependency performs both:

```text
JWT validation
```

and:

```text
server-side session validation
```

After decoding the access token, FastAPI reads the token's:

```text
sid
```

claim and loads that authentication session.

A usable session must remain active and must not be revoked, expired, or soft-deleted.

FastAPI then verifies:

```text
session.user_id == token.sub
```

If the token and session identify different users, authentication is rejected.

The authenticated user must also remain:

```text
is_active == true
deleted_at == null
```

This design means session revocation can invalidate an otherwise unexpired access token.

For example:

```text
access JWT still cryptographically valid
              |
              v
session revoked in PostgreSQL
              |
              v
protected request rejected
```

This is an intentional security property.

---

## 11. Authentication Session Records

Each successful login creates a new `Session` record.

Session metadata includes:

```text
user_id
user_agent
ip_address
device_name
last_seen_at
expires_at
is_active
revoked_at
revocation_reason
```

A session's initial expiry is aligned with the refresh-token lifetime.

During successful refresh, the session's:

```text
last_seen_at
expires_at
```

values are advanced to match the replacement refresh token.

Revocation changes the session to an inactive state and records a revocation timestamp and reason.

Examples of revocation reasons used by the application include:

```text
user_logout
user_logout_all
refresh_token_reuse
account_disabled
account_deactivated
```

Other account-lifecycle operations can also invalidate user access when appropriate.

---

## 12. Refresh Tokens

Refresh tokens are separate from JWT access tokens.

They are opaque credentials generated for session renewal.

The raw refresh token is returned to the caller only when it is issued. The database stores a digest rather than the reusable raw token.

The stored refresh-token record includes security state such as:

```text
user_id
session_id
token_digest
family_id
expires_at
used_at
revoked_at
replaced_by_token_id
```

The default refresh-token lifetime is:

```text
30 days
```

through:

```text
REFRESH_TOKEN_EXPIRE_DAYS
```

---

## 13. Refresh-Token Families

A successful login creates a new refresh-token family.

Conceptually:

```text
login
  |
  v
family A
  |
  +-- token A1
```

When token `A1` is refreshed:

```text
family A
  |
  +-- A1 [used]
  |
  +-- A2 [active]
```

The old token records:

```text
used_at
replaced_by_token_id
```

and the replacement remains in the same:

```text
family_id
```

This creates a server-side token lineage.

---

## 14. Refresh Rotation

Refresh tokens are single-use credentials.

A normal refresh performs the following sequence:

```text
receive raw refresh token
        |
        v
digest token
        |
        v
load stored record
        |
        v
reject used/revoked/expired token
        |
        v
validate active session
        |
        v
validate active user
        |
        v
generate replacement refresh token
        |
        v
mark old token used
        |
        v
link old token -> replacement
        |
        v
extend session
        |
        v
issue new access token
        |
        v
return new token pair
```

The client must replace both old credentials after successful refresh.

---

## 15. Refresh-Token Reuse Detection

If a refresh token is presented after it has already been used or revoked, the service treats the event as refresh-token reuse.

The backend then:

1. revokes the token family;
2. revokes the associated authentication session;
3. stores `refresh_token_reuse` as the session revocation reason;
4. rejects the refresh request.

Conceptually:

```text
A1 used legitimately
   |
   v
A2 issued

later:

A1 presented again
   |
   v
reuse detected
   |
   +--> revoke family A
   |
   +--> revoke session
   |
   v
authentication must restart
```

This limits the value of a stolen historical refresh token.

The backend is the authoritative reuse-detection boundary even when multiple browser contexts or application instances exist.

---

## 16. Expired Refresh Tokens

When a refresh token has reached its expiry:

```text
expires_at <= now
```

the backend marks the record revoked and rejects the request.

An expired refresh token cannot create a replacement access token or extend its session.

---

## 17. Invalid Sessions During Refresh

A refresh token cannot revive a session that is no longer active.

If the token references an invalid session:

* the refresh token is revoked;
* the refresh request is rejected.

Similarly, if the referenced user has become inactive or soft-deleted:

* the session is revoked;
* the refresh-token family is revoked;
* the refresh request is denied.

This prevents account deactivation from being bypassed by possession of an older refresh token.

---

## 18. Logout

### Current-session logout

`POST /api/v1/auth/logout` accepts a refresh token.

If the token exists, logout:

* revokes refresh tokens associated with that session;
* revokes the session;
* records `user_logout` as the session revocation reason.

If the supplied refresh token does not exist, logout behaves as a safe no-op instead of leaking token-existence information.

### Logout all

`POST /api/v1/auth/logout-all` requires an authenticated user.

It:

* revokes all refresh tokens belonging to the user;
* revokes all active authentication sessions belonging to the user;
* records `user_logout_all` as the session revocation reason.

Because protected access tokens depend on active server-side sessions, session revocation also prevents continued use of access JWTs linked to those sessions.

---

## 19. Account Deactivation and Deletion

Administrative account lifecycle changes are connected to authentication revocation.

When an account is deactivated, the user-administration service revokes:

```text
all refresh tokens for the user
all active authentication sessions for the user
```

When an account is soft-deleted, authentication state is similarly invalidated.

This means an administrator cannot deactivate or delete an account while allowing the account's already-issued session to remain usable.

Tests verify that after user deletion:

```text
GET /api/v1/auth/me
```

using the old access token fails, and:

```text
POST /api/v1/auth/refresh
```

using the previous refresh token also fails.

---

## 20. Email Verification Tokens

Email-verification tokens use dedicated persistence rather than being treated as login tokens.

The verification-token model tracks:

```text
user_id
token_digest
expires_at
consumed_at
revoked_at
```

The raw reusable token is not stored as the database credential.

The default verification lifetime is:

```text
24 hours
```

through:

```text
EMAIL_VERIFICATION_EXPIRE_HOURS
```

A verification token is usable only while it is:

```text
not consumed
not revoked
not expired
```

After successful consumption it cannot be reused.

---

## 21. Password Reset Tokens

Password-reset tokens follow the same one-time lifecycle pattern.

The database tracks:

```text
user_id
token_digest
expires_at
consumed_at
revoked_at
```

The default password-reset lifetime is:

```text
60 minutes
```

through:

```text
PASSWORD_RESET_EXPIRE_MINUTES
```

A reset token cannot be used after it has been:

```text
consumed
revoked
expired
```

Password reset replaces the user's password hash and resets failed-login/lockout state.

Existing authentication state is invalidated as part of the password-recovery security boundary so previously issued session credentials cannot continue to represent the recovered account indefinitely.

---

## 22. Password-History Scope

The current inspected implementation does not provide enough source evidence to document a persisted password-history mechanism as an implemented security control.

Therefore this documentation intentionally does **not** claim that previous password hashes are retained or that password reuse across historical passwords is currently blocked.

If password-history enforcement is added later, it should be documented only after:

* the persistence model exists;
* password-change/reset services enforce it;
* migrations exist;
* automated tests cover reuse rejection.

---

## 23. Next.js BFF Authentication Boundary

Administrator authentication is not performed directly from browser JavaScript against FastAPI.

Instead, the browser communicates with Next.js routes under:

```text
/api/admin-auth/*
```

The BFF communicates with FastAPI server-to-server.

The main files are:

```text
frontend/app/api/admin-auth/login/route.ts
frontend/app/api/admin-auth/logout/route.ts
frontend/app/api/admin-auth/refresh/route.ts
frontend/app/api/admin-auth/session/route.ts
frontend/lib/auth/constants.ts
frontend/lib/auth/server.ts
frontend/lib/auth/admin-proxy.ts
frontend/services/admin/client.ts
```

Production server-side backend calls use the server-only backend configuration and can communicate with the internal backend service without exposing that internal address to the browser.

---

## 24. Administrator Login Through Next.js

The browser posts administrator credentials to:

```text
POST /api/admin-auth/login
```

Next.js:

1. parses and validates the request;
2. normalizes the email address;
3. calls FastAPI `/auth/login` server-side;
4. receives the user and token pair;
5. verifies that the user is eligible for administrative access;
6. stores the credentials as HttpOnly cookies;
7. returns the authenticated user to the browser.

The token pair is not returned to browser JavaScript in the administrator login response.

### Administrative eligibility

The BFF rejects accounts that are:

```text
inactive
unverified
soft-deleted
```

A superuser is eligible.

A non-superuser is eligible when the account has at least one active, non-deleted role.

This permits role-scoped administrators such as editors and viewers to enter the administration application while FastAPI permissions determine which operations they may actually perform.

If FastAPI credentials are valid but the user does not qualify for administration, the login BFF performs best-effort cleanup by sending the newly created refresh token to the backend logout endpoint before returning an administrative-access error.

---

## 25. Authentication Cookies

The administrator BFF stores two cookies:

```text
akahalu_admin_access_token
akahalu_admin_refresh_token
```

Both cookies are configured with:

```text
HttpOnly = true
SameSite = Lax
Path     = /
```

In production:

```text
Secure = true
```

Cookie expiry is aligned with the corresponding backend token expiry.

Because the cookies are `HttpOnly`, normal client-side JavaScript cannot read their values.

This significantly reduces direct token exposure to browser-side application code.

### Cookie deletion

Logout or failed session recovery clears both cookies by overwriting them with expired values while retaining the relevant security attributes.

---

## 26. Administrator Session Endpoint

The browser can establish the current administrative state through:

```text
GET /api/admin-auth/session
```

The route follows this sequence:

```text
access cookie present?
        |
       yes
        |
        v
call FastAPI /auth/me
        |
 valid administrator?
        |
       yes ------> return user
        |
       no
        v
refresh cookie present?
        |
       no -------> clear cookies + 401
        |
       yes
        v
refresh with FastAPI
        |
 successful and administrator?
        |
       no -------> clear cookies + 401
        |
       yes
        v
set rotated cookies
        |
        v
return user
```

The browser therefore receives identity/session state rather than raw bearer tokens.

---

## 27. Administrator Refresh Endpoint

`POST /api/admin-auth/refresh` reads the HttpOnly refresh-token cookie.

If the cookie is missing:

* both authentication cookies are cleared;
* HTTP `401` is returned.

If backend refresh fails or the returned user is not administratively eligible:

* cookies are cleared;
* HTTP `401` is returned.

On success:

* FastAPI rotates the refresh token;
* Next.js receives the new pair;
* both cookies are replaced;
* the user object is returned.

---

## 28. Administrator Logout Endpoint

`POST /api/admin-auth/logout` reads the refresh token from the HttpOnly cookie and attempts server-side FastAPI logout.

Local cookies are cleared even if FastAPI is temporarily unavailable.

This ensures the browser's local authenticated state is removed even during a transient backend outage.

Backend revocation remains the authoritative server-side logout mechanism when reachable.

---

## 29. Authenticated Administrator Proxy

Protected Next.js administrator API routes use a reusable BFF proxy.

The proxy:

1. reads the HttpOnly access-token cookie;
2. forwards the request to FastAPI with `Authorization: Bearer ...`;
3. returns successful backend responses;
4. when access authentication returns `401`, attempts refresh using the HttpOnly refresh cookie;
5. receives rotated tokens;
6. retries the original protected request;
7. updates authentication cookies.

This allows short access-token lifetimes without forcing normal administrator navigation to fail when a valid refresh session still exists.

---

## 30. Refresh Concurrency

The frontend administrator client includes an in-flight refresh promise so concurrent requests in the same JavaScript runtime can share a refresh operation instead of independently consuming the same single-use refresh token.

This protection is intentionally scoped.

It can coordinate requests within the same runtime, but it should not be treated as a distributed lock across:

```text
multiple browser tabs
multiple browser processes
multiple Next.js instances
multiple devices
```

The backend refresh-family reuse mechanism remains the authoritative security control when simultaneous token use crosses those boundaries.

---

## 31. Authentication Error Semantics

Important backend authentication errors include:

```text
invalid_credentials
account_disabled
email_not_verified
account_locked
invalid_refresh_token
refresh_token_reuse
invalid_session
invalid_authentication
```

Typical HTTP semantics are:

```text
401 -> authentication credential/token failure
403 -> authenticated identity/account state is forbidden
423 -> temporary account lockout
```

Protected routes also set the Bearer authentication challenge when authentication credentials are invalid.

---

## 32. Security Configuration

Authentication-related backend configuration includes:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ISSUER
JWT_AUDIENCE

ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS

EMAIL_VERIFICATION_EXPIRE_HOURS
PASSWORD_RESET_EXPIRE_MINUTES

MAXIMUM_FAILED_LOGIN_ATTEMPTS
ACCOUNT_LOCKOUT_MINUTES
```

`JWT_SECRET_KEY` must be a high-entropy environment-specific secret.

It must never be:

```text
committed to Git
embedded in a Docker image
included in frontend public environment variables
printed in CI logs
shared between unrelated environments without deliberate policy
```

Production secrets are supplied externally through deployment environment configuration.

---

## 33. Production Transport and Host Controls

Authentication is designed to operate behind the production Nginx boundary.

Production configuration requires:

```text
DEBUG = false
non-wildcard trusted hosts
non-wildcard allowed origins
no localhost HTTP origin as a production browser origin
```

API documentation is disabled by default in the production environment unless explicitly overridden.

Authentication cookies use the Secure attribute when the Next.js application runs in production mode, so the public production deployment must be served over HTTPS.

---

## 34. Security Boundaries

The following are important architectural boundaries.

### FastAPI is authoritative

Next.js convenience checks do not replace FastAPI authentication.

FastAPI remains responsible for:

```text
credential validation
JWT issuance
JWT validation
refresh-token persistence
refresh rotation
reuse detection
session persistence
session revocation
account-state validation
```

### PostgreSQL participates in authentication

Authentication is not fully stateless.

A valid JWT requires a valid server-side authentication session.

This allows immediate session revocation for events such as:

```text
logout
logout-all
refresh-token reuse
account deactivation
account deletion
password recovery
```

### Browser authorization state is not trusted

The browser may know the current user's roles and permissions for user-interface purposes, but the browser never becomes the authoritative security boundary.

Protected operations must continue to be authenticated and authorized on FastAPI.

---

## 35. Security Properties

The current implementation provides the following major authentication properties:

```text
passwords stored as secure hashes
short-lived signed access JWTs
issuer and audience validation
database-backed access-token sessions
opaque refresh credentials
digest-only refresh-token persistence
single-use refresh rotation
refresh-token family lineage
refresh-token reuse detection
session revocation
logout-all support
failed-login tracking
temporary account lockout
verified-account login requirement
disabled/deleted-account rejection
one-time account lifecycle tokens
HttpOnly administrator cookies
Secure production cookies
SameSite cookie protection
server-side administrator BFF
backend-enforced authentication
```

---

## 36. Testing

Authentication behavior is covered by dedicated tests including:

```text
backend/tests/integration/test_authentication_api.py
backend/tests/integration/test_account_lifecycle_api.py
backend/tests/integration/test_password_reset_api.py
backend/tests/integration/test_admin_users_api.py
backend/tests/unit/test_passwords.py
backend/tests/unit/test_tokens.py
backend/tests/unit/test_account_tokens.py
backend/tests/unit/test_authorization.py
```

The test suite should continue to cover at minimum:

* valid login;
* invalid login;
* unknown accounts;
* inactive accounts;
* unverified accounts;
* lockout threshold;
* successful lockout recovery;
* access-token validation;
* invalid and expired tokens;
* session revocation;
* refresh rotation;
* refresh-token reuse;
* logout;
* logout-all;
* email-verification token lifecycle;
* password-reset token lifecycle;
* access revocation after account deactivation/deletion;
* administrator BFF session recovery.

---

## 37. Rules for Future Authentication Changes

Future authentication changes should preserve these principles:

1. Never place raw authentication tokens in browser localStorage or sessionStorage.
2. Never weaken FastAPI authentication to accommodate frontend behavior.
3. Never store raw refresh, verification, or reset tokens in PostgreSQL when a digest can be stored instead.
4. Keep access tokens short-lived.
5. Preserve database-backed session validation.
6. Rotate refresh tokens on use.
7. Treat refresh-token reuse as a security event.
8. Revoke authentication state when an account loses access.
9. Keep secrets outside source control and image build context.
10. Add regression tests for every authentication security change.
11. Do not document controls as implemented until the implementation and tests exist.
12. Keep frontend authentication checks supplementary to the FastAPI security boundary.

---

## 38. Related Documentation

See:

```text
docs/security/authorization.md
docs/architecture/backend-architecture.md
docs/architecture/frontend-architecture.md
docs/architecture/system-overview.md
docs/database/data-model.md
docs/deployment/environment-variables.md
docs/deployment/production-runbook.md
```
