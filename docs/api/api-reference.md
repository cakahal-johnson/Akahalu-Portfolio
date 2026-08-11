# Akahalu Portfolio — API Reference

## 1. Overview

Akahalu Portfolio exposes a versioned FastAPI application for:

* application health;
* authentication;
* account lifecycle;
* public contact submissions;
* public portfolio content;
* portfolio administration;
* contact-inquiry administration;
* user administration;
* role-based access control.

The current OpenAPI contract contains:

```text
API title:          Akahalu Portfolio API
API version:        1.0.0
Documented paths:   73
HTTP operations:    99
OpenAPI schemas:    127
```

The main versioned API prefix is:

```text
/api/v1
```

The unversioned application root:

```text
/
```

is also exposed.

---

# 2. Base URLs

## Local backend development

```text
http://127.0.0.1:8000/api/v1
```

## Local production-stack smoke test

Through Nginx:

```text
http://localhost:8080/api/v1
```

## Production

Expected same-domain form:

```text
https://<portfolio-domain>/api/v1
```

Example:

```text
https://portfolio.example.com/api/v1
```

---

# 3. API Versioning

All normal backend application APIs are mounted beneath:

```text
/api/v1
```

Router composition is:

```text
FastAPI
  |
  +-- /
  |
  +-- /api/v1
        |
        +-- health
        +-- authentication
        +-- account lifecycle
        +-- RBAC
        +-- admin users
        +-- contact
        +-- public portfolio
        +-- admin portfolio
```

The version prefix is configured through:

```text
API_V1_PREFIX
```

with the current value:

```text
/api/v1
```

Changing this prefix is an API architecture change and requires coordinated changes to:

* Nginx;
* frontend environment configuration;
* BFF/server services;
* tests;
* documentation.

---

# 4. Production OpenAPI Policy

FastAPI can generate an OpenAPI schema internally from the application contract.

Interactive documentation is available when API documentation is enabled.

Development-style endpoints are normally:

```text
/docs
/openapi.json
```

Production configuration uses:

```text
ENVIRONMENT=production
API_DOCS_ENABLED=false
```

The validated production behavior is:

```text
/docs         -> 404
/openapi.json -> 404
```

The absence of public Swagger/OpenAPI endpoints in production does not remove request validation or response models from the application.

---

# 5. Authentication Scheme

Protected FastAPI endpoints use HTTP Bearer authentication.

OpenAPI security scheme:

```text
HTTPBearer
```

Type:

```text
http
```

Scheme:

```text
bearer
```

A protected request uses:

```http
Authorization: Bearer <access-token>
```

The access token alone is not the complete authentication boundary.

FastAPI also validates the corresponding server-side authentication session.

See:

```text
docs/security/authentication.md
```

---

# 6. Authorization

Authentication and permissions are separate concerns.

A protected endpoint may require:

```text
HTTP Bearer authentication
+
a specific application permission
```

Current canonical permissions are:

```text
projects.read
projects.create
projects.update
projects.delete

profile.read
profile.create
profile.update
profile.delete

experience.read
experience.create
experience.update
experience.delete

contact_inquiries.read
contact_inquiries.update
contact_inquiries.delete

users.manage
roles.manage
```

The `is_superuser` backend path bypasses explicit role/permission assignments after successful authentication.

See:

```text
docs/security/authorization.md
```

---

# 7. HTTP Status Conventions

Common successful status codes include:

```text
200 OK
201 Created
204 No Content
```

Common failure responses include:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Content
423 Locked
503 Service Unavailable
```

Not every runtime domain error is explicitly enumerated in every generated OpenAPI operation.

For example, FastAPI automatically documents request-validation `422` responses, while domain services may additionally produce:

```text
404
409
```

or other application-specific statuses.

---

# 8. Application Error Shape

Many application/domain errors use:

```json
{
  "detail": {
    "code": "machine_readable_error_code",
    "message": "Human-readable explanation."
  }
}
```

Examples include:

```text
invalid_authentication
insufficient_permissions
project_not_found
profile_not_found
experience_not_found
email_already_registered
invalid_verification_token
invalid_password_reset_token
```

Authentication failures may also include a Bearer authentication challenge.

---

# 9. Validation Errors

Pydantic/FastAPI request-validation failures use the standard FastAPI validation structure.

Typical status:

```text
422 Unprocessable Content
```

OpenAPI schemas include:

```text
HTTPValidationError
ValidationError
```

Validation can occur for:

* malformed UUIDs;
* invalid enums;
* missing required fields;
* invalid email addresses;
* invalid URLs;
* string-length violations;
* pagination bounds;
* slug patterns;
* invalid dates;
* domain field constraints.

---

# 10. Pagination

Paginated APIs generally return:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total_items": 0,
  "total_pages": 0,
  "has_next_page": false,
  "has_previous_page": false
}
```

Common query parameters:

```text
page
page_size
```

Typical constraints:

```text
page      >= 1
page_size >= 1
page_size <= 100
```

Domain-specific filters are documented in the relevant sections below.

---

# 11. Root Endpoint

## `GET /`

Authentication:

```text
None
```

Purpose:

```text
API root
```

Success:

```text
200 OK
```

This endpoint is outside `/api/v1`.

---

# 12. Health API

All health endpoints are public.

## `GET /api/v1/health`

Purpose:

```text
General API health.
```

Authentication:

```text
None
```

Response model:

```text
HealthResponse
```

Example shape:

```json
{
  "status": "healthy",
  "service": "portfolio-api",
  "environment": "production",
  "timestamp": "2026-08-11T00:00:00Z"
}
```

---

## `GET /api/v1/health/live`

Purpose:

```text
Determine whether the FastAPI process is alive.
```

Authentication:

```text
None
```

Response:

```text
HealthResponse
```

This endpoint does not perform dependency readiness checks.

---

## `GET /api/v1/health/ready`

Purpose:

```text
Determine whether the application and required dependencies are ready.
```

Authentication:

```text
None
```

Dependencies checked:

```text
PostgreSQL
Redis
```

Healthy response model:

```text
ReadinessResponse
```

Example:

```json
{
  "status": "healthy",
  "service": "portfolio-api",
  "environment": "production",
  "timestamp": "2026-08-11T00:00:00Z",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

If either dependency is unhealthy:

```text
503 Service Unavailable
```

is returned.

---

# 13. Authentication API

Base:

```text
/api/v1/auth
```

---

## `POST /api/v1/auth/login`

Authentication:

```text
None
```

Request:

```text
LoginRequest
```

Principal fields include:

```text
email
password
device_name
```

Response:

```text
LoginResponse
```

The response contains the authenticated user and a token pair.

Success:

```text
200 OK
```

Important runtime failures can include:

```text
401 invalid credentials
403 disabled/unverified account
423 temporary account lockout
```

---

## `POST /api/v1/auth/refresh`

Authentication:

```text
Refresh credential supplied in request body
```

Request:

```text
RefreshRequest
```

Principal field:

```text
refresh_token
```

Response:

```text
RefreshResponse
```

A successful refresh rotates the refresh token.

Success:

```text
200 OK
```

Refresh tokens are single-use and participate in refresh-family reuse detection.

---

## `POST /api/v1/auth/logout`

Authentication:

```text
Refresh credential supplied in request body
```

Request:

```text
LogoutRequest
```

Success:

```text
204 No Content
```

The relevant authentication session and refresh state are revoked when the supplied token resolves to a known session.

---

## `POST /api/v1/auth/logout-all`

Authentication:

```text
Bearer
```

Permission:

```text
No separate RBAC permission.
```

Success:

```text
204 No Content
```

Revokes active authentication sessions and refresh state for the authenticated user.

---

## `GET /api/v1/auth/me`

Authentication:

```text
Bearer
```

Permission:

```text
No separate RBAC permission.
```

Response:

```text
UserRead
```

Success:

```text
200 OK
```

This endpoint validates both:

```text
access token
server-side session
```

before returning the authenticated user.

---

# 14. Account Lifecycle API

Base:

```text
/api/v1/account
```

These routes are public credential/lifecycle routes rather than bearer-protected administration endpoints.

---

## `POST /api/v1/account/register`

Request:

```text
RegisterRequest
```

Principal fields:

```text
email
password
first_name
last_name
display_name
```

Response:

```text
RegisterResponse
```

Success:

```text
201 Created
```

A duplicate email may produce:

```text
409 email_already_registered
```

Current response behavior can include:

```text
verification_token
verification_token_expires_at
```

for the generated verification flow.

---

## `POST /api/v1/account/verify-email`

Request:

```text
VerifyEmailRequest
```

Principal field:

```text
token
```

Response:

```text
VerifyEmailResponse
```

Success:

```text
200 OK
```

Possible domain failures include:

```text
400 invalid_verification_token
403 inactive_account
```

---

## `POST /api/v1/account/resend-verification`

Request:

```text
ResendVerificationRequest
```

Principal field:

```text
email
```

Response:

```text
ResendVerificationResponse
```

Success:

```text
200 OK
```

The route deliberately returns a generic message when the account is absent or ineligible so that callers cannot reliably enumerate accounts.

The current response contract can include a newly generated verification token when one is issued.

---

## `POST /api/v1/account/forgot-password`

Request:

```text
ForgotPasswordRequest
```

Principal field:

```text
email
```

Response:

```text
ForgotPasswordResponse
```

Success:

```text
200 OK
```

The route uses a generic message regardless of whether an eligible account exists.

Current response behavior can include:

```text
reset_token
reset_token_expires_at
```

when a reset token is generated.

---

## `POST /api/v1/account/reset-password`

Request:

```text
ResetPasswordRequest
```

Principal fields:

```text
token
new_password
```

Response:

```text
ResetPasswordResponse
```

Success:

```text
200 OK
```

Possible failures include:

```text
400 invalid_password_reset_token
403 inactive_account
```

---

# 15. Account-Lifecycle Production Review Item

The current API implementation exposes generated verification/reset token values in lifecycle responses when those values are created.

This supports the current development/test workflow.

Before unrestricted public account self-service is enabled in a final production launch, review whether these raw lifecycle token fields should instead be delivered only through the intended out-of-band communication channel.

This is a deployment/security review item rather than an undocumented behavior.

---

# 16. Public Contact API

## `POST /api/v1/contact/inquiries`

Authentication:

```text
None
```

Request:

```text
ContactInquiryPublicCreate
```

Response:

```text
ContactInquiryPublicResponse
```

Success:

```text
201 Created
```

The service applies contact-submission protections including:

```text
duplicate detection
honeypot detection
privacy-preserving request metadata
```

Duplicate and honeypot submissions intentionally receive the same generic accepted-style response as ordinary accepted submissions.

This prevents the endpoint from disclosing spam-protection behavior.

---

# 17. Public Portfolio — Categories

All public portfolio category APIs require no authentication.

## `GET /api/v1/portfolio/categories`

Returns:

```text
active
non-deleted
publicly usable
```

project categories.

Response:

```text
list[ProjectCategoryRead]
```

Success:

```text
200 OK
```

---

## `GET /api/v1/portfolio/categories/{slug}`

Path parameter:

```text
slug
```

Response:

```text
ProjectCategoryRead
```

Success:

```text
200 OK
```

Inactive, deleted, or unknown categories are represented as unavailable/not found.

---

# 18. Public Portfolio — Technologies

## `GET /api/v1/portfolio/technologies`

Authentication:

```text
None
```

Optional query:

```text
category
```

The category uses the `ProjectTechnologyCategory` enum.

Response:

```text
list[ProjectTechnologyRead]
```

Only active, non-deleted technologies are returned.

---

## `GET /api/v1/portfolio/technologies/{slug}`

Authentication:

```text
None
```

Path parameter:

```text
slug
```

Response:

```text
ProjectTechnologyRead
```

Inactive, deleted, or unknown technologies are not exposed.

---

# 19. Public Portfolio — Projects

## `GET /api/v1/portfolio/projects`

Authentication:

```text
None
```

Query parameters:

```text
page
page_size
search
category_slug
technology_slug
is_featured
```

Defaults:

```text
page      = 1
page_size = 20
```

Maximum page size:

```text
100
```

Public records must satisfy the backend publication rules.

Conceptually:

```text
not deleted
published
public visibility
published_at exists
```

Response:

```text
PaginatedResponse<ProjectSummary>
```

---

## `GET /api/v1/portfolio/projects/featured`

Authentication:

```text
None
```

Query:

```text
limit
```

Default:

```text
6
```

Range:

```text
1..20
```

Response:

```text
list[ProjectSummary]
```

---

## `GET /api/v1/portfolio/projects/{slug}`

Authentication:

```text
None
```

Path:

```text
slug
```

Response:

```text
ProjectRead
```

Only eligible public projects are returned.

Unknown or unavailable projects produce a public not-found response.

---

# 20. Public Portfolio — Profile

## `GET /api/v1/portfolio/profile`

Authentication:

```text
None
```

Response:

```text
ProfileRead
```

Only the public, non-deleted singleton profile is exposed.

Private, missing, and deleted profile states are represented as unavailable/not found.

---

# 21. Public Portfolio — Experience

## `GET /api/v1/portfolio/experiences`

Authentication:

```text
None
```

Query parameters:

```text
page
page_size
search
employment_type
location_type
is_current
is_featured
```

Defaults:

```text
page      = 1
page_size = 20
```

Maximum page size:

```text
100
```

Response:

```text
PaginatedResponse<ExperienceSummary>
```

Only public, non-deleted experience records are returned.

---

## `GET /api/v1/portfolio/experiences/featured`

Authentication:

```text
None
```

Query:

```text
limit
```

Default:

```text
6
```

Range:

```text
1..20
```

Response:

```text
list[ExperienceSummary]
```

---

## `GET /api/v1/portfolio/experiences/{slug}`

Authentication:

```text
None
```

Response:

```text
ExperienceRead
```

Unknown or non-public records return a not-found response.

---

# 22. Administrative API Rules

Unless otherwise noted, administrative operations require:

```text
HTTP Bearer authentication
```

plus the permission shown for the operation.

The frontend administration interface normally accesses these endpoints through the Next.js BFF rather than exposing raw bearer tokens to browser JavaScript.

---

# 23. Admin Contact Inquiries

Base:

```text
/api/v1/admin/contact/inquiries
```

## Endpoint matrix

| Method | Path                                               | Permission                 | Request                        |
| ------ | -------------------------------------------------- | -------------------------- | ------------------------------ |
| GET    | `/admin/contact/inquiries`                         | `contact_inquiries.read`   | Query filters                  |
| GET    | `/admin/contact/inquiries/statistics`              | `contact_inquiries.read`   | —                              |
| GET    | `/admin/contact/inquiries/assignees`               | `contact_inquiries.read`   | —                              |
| GET    | `/admin/contact/inquiries/projects`                | `contact_inquiries.read`   | —                              |
| GET    | `/admin/contact/inquiries/{inquiry_id}`            | `contact_inquiries.read`   | `include_deleted`              |
| PATCH  | `/admin/contact/inquiries/{inquiry_id}`            | `contact_inquiries.update` | `ContactInquiryUpdate`         |
| PATCH  | `/admin/contact/inquiries/{inquiry_id}/read-state` | `contact_inquiries.update` | `ContactInquiryReadUpdate`     |
| PATCH  | `/admin/contact/inquiries/{inquiry_id}/status`     | `contact_inquiries.update` | `ContactInquiryStatusUpdate`   |
| POST   | `/admin/contact/inquiries/{inquiry_id}/restore`    | `contact_inquiries.update` | `ContactInquiryRestoreRequest` |
| DELETE | `/admin/contact/inquiries/{inquiry_id}`            | `contact_inquiries.delete` | `ContactInquiryDeleteRequest`  |

All paths in this table are relative to:

```text
/api/v1
```

---

## Admin inquiry list filters

`GET /api/v1/admin/contact/inquiries`

supports:

```text
page
page_size
search

inquiry_type
inquiry_status
priority
is_read

assigned_to_id
project_id
include_unassigned

include_deleted

created_from
created_to

sort_by
sort_direction
```

Default pagination:

```text
page      = 1
page_size = 20
```

Maximum:

```text
100
```

Search includes fields such as:

```text
sender name
email
company
subject
message
internal notes
```

---

## Inquiry sorting

Supported administrative sort fields include:

```text
name
email
subject
inquiry_type
status
priority
is_read
created_at
updated_at
```

Direction:

```text
asc
desc
```

---

## Inquiry statistics

`GET /api/v1/admin/contact/inquiries/statistics`

returns counts such as:

```text
new
in_progress
responded
closed
spam
unread
requires_attention
```

---

## Assignee and project option endpoints

These routes intentionally use:

```text
contact_inquiries.read
```

rather than broader user/project administration permissions:

```text
GET /api/v1/admin/contact/inquiries/assignees
GET /api/v1/admin/contact/inquiries/projects
```

They return lightweight data required to understand and administer inquiries.

---

# 24. Admin Portfolio Categories

Base:

```text
/api/v1/admin/portfolio/categories
```

| Method | Path                                                | Permission        | Request                         |
| ------ | --------------------------------------------------- | ----------------- | ------------------------------- |
| GET    | `/admin/portfolio/categories`                       | `projects.read`   | Query filters                   |
| POST   | `/admin/portfolio/categories`                       | `projects.create` | `ProjectCategoryCreate`         |
| GET    | `/admin/portfolio/categories/{category_id}`         | `projects.read`   | `include_deleted`               |
| PATCH  | `/admin/portfolio/categories/{category_id}`         | `projects.update` | `ProjectCategoryUpdate`         |
| PATCH  | `/admin/portfolio/categories/{category_id}/status`  | `projects.update` | `ProjectCategoryStatusUpdate`   |
| POST   | `/admin/portfolio/categories/{category_id}/restore` | `projects.update` | `ProjectCategoryRestoreRequest` |
| DELETE | `/admin/portfolio/categories/{category_id}`         | `projects.delete` | `ProjectCategoryDeleteRequest`  |

List query parameters:

```text
page
page_size
search
is_active
include_deleted
sort_by
sort_direction
```

List response:

```text
PaginatedResponse<ProjectCategoryAdminRead>
```

Mutation/detail response:

```text
ProjectCategoryAdminRead
```

---

# 25. Admin Portfolio Technologies

Base:

```text
/api/v1/admin/portfolio/technologies
```

| Method | Path                                                    | Permission        | Request                           |
| ------ | ------------------------------------------------------- | ----------------- | --------------------------------- |
| GET    | `/admin/portfolio/technologies`                         | `projects.read`   | Query filters                     |
| POST   | `/admin/portfolio/technologies`                         | `projects.create` | `ProjectTechnologyCreate`         |
| GET    | `/admin/portfolio/technologies/{technology_id}`         | `projects.read`   | `include_deleted`                 |
| PATCH  | `/admin/portfolio/technologies/{technology_id}`         | `projects.update` | `ProjectTechnologyUpdate`         |
| PATCH  | `/admin/portfolio/technologies/{technology_id}/status`  | `projects.update` | `ProjectTechnologyStatusUpdate`   |
| POST   | `/admin/portfolio/technologies/{technology_id}/restore` | `projects.update` | `ProjectTechnologyRestoreRequest` |
| DELETE | `/admin/portfolio/technologies/{technology_id}`         | `projects.delete` | `ProjectTechnologyDeleteRequest`  |

List query parameters:

```text
page
page_size
search
category
is_active
include_deleted
sort_by
sort_direction
```

List response:

```text
PaginatedResponse<ProjectTechnologyAdminRead>
```

Detail/mutation response:

```text
ProjectTechnologyAdminRead
```

---

# 26. Admin Portfolio Projects

Base:

```text
/api/v1/admin/portfolio/projects
```

| Method | Path                                                | Permission        | Request                   |
| ------ | --------------------------------------------------- | ----------------- | ------------------------- |
| GET    | `/admin/portfolio/projects`                         | `projects.read`   | Query filters             |
| POST   | `/admin/portfolio/projects`                         | `projects.create` | `ProjectCreate`           |
| GET    | `/admin/portfolio/projects/{project_id}`            | `projects.read`   | `include_deleted`         |
| PATCH  | `/admin/portfolio/projects/{project_id}`            | `projects.update` | `ProjectUpdate`           |
| PATCH  | `/admin/portfolio/projects/{project_id}/featured`   | `projects.update` | `ProjectFeaturedUpdate`   |
| PATCH  | `/admin/portfolio/projects/{project_id}/status`     | `projects.update` | `ProjectStatusUpdate`     |
| PATCH  | `/admin/portfolio/projects/{project_id}/visibility` | `projects.update` | `ProjectVisibilityUpdate` |
| POST   | `/admin/portfolio/projects/{project_id}/restore`    | `projects.update` | `ProjectRestoreRequest`   |
| DELETE | `/admin/portfolio/projects/{project_id}`            | `projects.delete` | `ProjectDeleteRequest`    |

---

## Project list filters

```text
page
page_size
search
category_id
project_status
visibility
is_featured
technology_id
include_deleted
sort_by
sort_direction
```

List response:

```text
PaginatedResponse<ProjectAdminRead>
```

Detail/mutation response:

```text
ProjectAdminRead
```

---

# 27. Admin Project Links

Project links use the general project permission family.

Base pattern:

```text
/api/v1/admin/portfolio/projects/{project_id}/links
```

| Method | Path                                                             | Permission        | Request                             |
| ------ | ---------------------------------------------------------------- | ----------------- | ----------------------------------- |
| GET    | `/admin/portfolio/projects/{project_id}/links`                   | `projects.read`   | Query filters                       |
| POST   | `/admin/portfolio/projects/{project_id}/links`                   | `projects.create` | `ProjectLinkCreate`                 |
| GET    | `/admin/portfolio/projects/{project_id}/links/{link_id}`         | `projects.read`   | `include_deleted`                   |
| PATCH  | `/admin/portfolio/projects/{project_id}/links/{link_id}`         | `projects.update` | `ProjectLinkUpdate`                 |
| PATCH  | `/admin/portfolio/projects/{project_id}/links/{link_id}/status`  | `projects.update` | `ProjectLinkStatusUpdate`           |
| POST   | `/admin/portfolio/projects/{project_id}/links/{link_id}/restore` | `projects.update` | `ProjectLinkRestoreRequest`         |
| DELETE | `/admin/portfolio/projects/{project_id}/links/{link_id}`         | `projects.delete` | Optional `ProjectLinkDeleteRequest` |

Link list filters:

```text
page
page_size
search
link_type
is_active
opens_in_new_tab
include_deleted
sort_by
sort_direction
```

List response:

```text
PaginatedResponse<ProjectLinkAdminRead>
```

Detail/mutation response:

```text
ProjectLinkAdminRead
```

The DELETE request body is currently optional according to the generated OpenAPI contract.

---

# 28. Admin Project Media

Media uses the general project permission family.

## Collection routes

```text
/api/v1/admin/portfolio/projects/{project_id}/media
```

| Method | Path                                           | Permission        | Request              |
| ------ | ---------------------------------------------- | ----------------- | -------------------- |
| GET    | `/admin/portfolio/projects/{project_id}/media` | `projects.read`   | Query filters        |
| POST   | `/admin/portfolio/projects/{project_id}/media` | `projects.create` | `ProjectMediaCreate` |

List query parameters:

```text
page
page_size
search
media_type
is_primary
include_deleted
sort_by
sort_direction
```

---

## Individual media routes

Base:

```text
/api/v1/admin/portfolio/media/{media_id}
```

| Method | Path                                        | Permission        | Request                      |
| ------ | ------------------------------------------- | ----------------- | ---------------------------- |
| GET    | `/admin/portfolio/media/{media_id}`         | `projects.read`   | `include_deleted`            |
| PATCH  | `/admin/portfolio/media/{media_id}`         | `projects.update` | `ProjectMediaUpdate`         |
| PATCH  | `/admin/portfolio/media/{media_id}/primary` | `projects.update` | `ProjectMediaPrimaryUpdate`  |
| POST   | `/admin/portfolio/media/{media_id}/restore` | `projects.update` | `ProjectMediaRestoreRequest` |
| DELETE | `/admin/portfolio/media/{media_id}`         | `projects.delete` | `ProjectMediaDeleteRequest`  |

List response:

```text
PaginatedResponse<ProjectMediaAdminRead>
```

Detail/mutation response:

```text
ProjectMediaAdminRead
```

---

# 29. Admin Portfolio Profile

Base:

```text
/api/v1/admin/portfolio/profile
```

The profile is a singleton resource.

| Method | Path                                  | Permission       | Request                   |
| ------ | ------------------------------------- | ---------------- | ------------------------- |
| GET    | `/admin/portfolio/profile`            | `profile.read`   | `include_deleted`         |
| POST   | `/admin/portfolio/profile`            | `profile.create` | `ProfileCreate`           |
| PATCH  | `/admin/portfolio/profile`            | `profile.update` | `ProfileUpdate`           |
| PATCH  | `/admin/portfolio/profile/visibility` | `profile.update` | `ProfileVisibilityUpdate` |
| POST   | `/admin/portfolio/profile/restore`    | `profile.update` | `ProfileRestoreRequest`   |
| DELETE | `/admin/portfolio/profile`            | `profile.delete` | `ProfileDeleteRequest`    |

Response:

```text
ProfileAdminRead
```

Important domain states can produce:

```text
404 profile_not_found
409 profile_deleted
409 profile_already_exists
422 profile_validation_error
```

depending on the operation.

---

# 30. Admin Portfolio Experiences

Base:

```text
/api/v1/admin/portfolio/experiences
```

| Method | Path                                                      | Permission          | Request                      |
| ------ | --------------------------------------------------------- | ------------------- | ---------------------------- |
| GET    | `/admin/portfolio/experiences`                            | `experience.read`   | Query filters                |
| POST   | `/admin/portfolio/experiences`                            | `experience.create` | `ExperienceCreate`           |
| GET    | `/admin/portfolio/experiences/{experience_id}`            | `experience.read`   | `include_deleted`            |
| PATCH  | `/admin/portfolio/experiences/{experience_id}`            | `experience.update` | `ExperienceUpdate`           |
| PATCH  | `/admin/portfolio/experiences/{experience_id}/featured`   | `experience.update` | `ExperienceFeaturedUpdate`   |
| PATCH  | `/admin/portfolio/experiences/{experience_id}/visibility` | `experience.update` | `ExperienceVisibilityUpdate` |
| POST   | `/admin/portfolio/experiences/{experience_id}/restore`    | `experience.update` | `ExperienceRestoreRequest`   |
| DELETE | `/admin/portfolio/experiences/{experience_id}`            | `experience.delete` | `ExperienceDeleteRequest`    |

List query parameters:

```text
page
page_size
search
employment_type
location_type
is_current
is_public
is_featured
include_deleted
sort_by
sort_direction
```

List response:

```text
PaginatedResponse<ExperienceAdminRead>
```

Detail/mutation response:

```text
ExperienceAdminRead
```

---

# 31. Admin Users

Base:

```text
/api/v1/admin/users
```

All current user-administration operations require:

```text
users.manage
```

There is no separate current canonical:

```text
users.read
```

permission.

| Method | Path                             | Permission     | Request                   |
| ------ | -------------------------------- | -------------- | ------------------------- |
| GET    | `/admin/users`                   | `users.manage` | Query filters             |
| GET    | `/admin/users/{user_id}`         | `users.manage` | `include_deleted`         |
| PATCH  | `/admin/users/{user_id}/status`  | `users.manage` | `AdminUserStatusUpdate`   |
| POST   | `/admin/users/{user_id}/restore` | `users.manage` | `AdminUserRestoreRequest` |
| DELETE | `/admin/users/{user_id}`         | `users.manage` | `AdminUserDeleteRequest`  |

---

## User list filters

```text
page
page_size
search
status
is_verified
is_superuser
include_deleted
sort_by
sort_direction
```

Response schemas include:

```text
AdminUserListResponse
AdminUserSummary
AdminUserDetail
```

Administrative lifecycle protections also prevent unsafe operations such as:

```text
self-deactivation
self-deletion
removing the last active administrator
```

where applicable.

Account deactivation/deletion also revokes existing authentication state.

---

# 32. RBAC API

Base:

```text
/api/v1/rbac
```

Every current RBAC operation requires:

```text
roles.manage
```

unless the authenticated user succeeds through the superuser bypass.

---

## `GET /api/v1/rbac/permissions`

Permission:

```text
roles.manage
```

Response:

```text
list[PermissionRead]
```

Success:

```text
200 OK
```

---

## `GET /api/v1/rbac/roles`

Permission:

```text
roles.manage
```

Response:

```text
list[RoleRead]
```

---

## `POST /api/v1/rbac/roles`

Permission:

```text
roles.manage
```

Request:

```text
RoleCreate
```

Response:

```text
RoleRead
```

Success:

```text
201 Created
```

---

## `PATCH /api/v1/rbac/roles/{role_id}`

Permission:

```text
roles.manage
```

Request:

```text
RoleUpdate
```

Response:

```text
RoleRead
```

Protected system roles may reject unsafe changes.

---

## `PUT /api/v1/rbac/roles/{role_id}/permissions`

Permission:

```text
roles.manage
```

Request:

```text
RolePermissionUpdate
```

Response:

```text
RoleRead
```

Replaces the role's current permission assignment with the supplied set.

Protected role invariants remain enforced by the backend.

---

## `GET /api/v1/rbac/users/{user_id}/roles`

Permission:

```text
roles.manage
```

Response:

```text
list[RoleRead]
```

---

## `PUT /api/v1/rbac/users/{user_id}/roles`

Permission:

```text
roles.manage
```

Request:

```text
UserRoleUpdate
```

Replaces the user's assigned roles with the supplied role set.

---

# 33. Administrative Permission Summary

| Domain            | Read                     | Create              | Update                     | Delete                     |
| ----------------- | ------------------------ | ------------------- | -------------------------- | -------------------------- |
| Projects          | `projects.read`          | `projects.create`   | `projects.update`          | `projects.delete`          |
| Categories        | `projects.read`          | `projects.create`   | `projects.update`          | `projects.delete`          |
| Technologies      | `projects.read`          | `projects.create`   | `projects.update`          | `projects.delete`          |
| Project links     | `projects.read`          | `projects.create`   | `projects.update`          | `projects.delete`          |
| Project media     | `projects.read`          | `projects.create`   | `projects.update`          | `projects.delete`          |
| Profile           | `profile.read`           | `profile.create`    | `profile.update`           | `profile.delete`           |
| Experience        | `experience.read`        | `experience.create` | `experience.update`        | `experience.delete`        |
| Contact inquiries | `contact_inquiries.read` | —                   | `contact_inquiries.update` | `contact_inquiries.delete` |
| Users             | `users.manage`           | `users.manage`      | `users.manage`             | `users.manage`             |
| RBAC              | `roles.manage`           | `roles.manage`      | `roles.manage`             | `roles.manage`             |

Restoration and state-transition operations generally use the corresponding update permission.

---

# 34. Public vs Administrative Visibility

Public APIs do not simply expose the same records as administrative APIs.

Public services enforce domain eligibility.

Examples include:

### Projects

Public projects must satisfy publication and visibility rules.

### Categories

Only active, non-deleted categories are exposed.

### Technologies

Only active, non-deleted technologies are exposed.

### Profile

Only the public, non-deleted singleton profile is exposed.

### Experience

Only public, non-deleted experience is exposed.

Therefore a record returning successfully from an administrative detail endpoint does not imply it is available through a public endpoint.

---

# 35. Soft Deletion

Several administrative APIs use soft deletion.

Typical lifecycle:

```text
active
  |
  | DELETE
  v
soft deleted
  |
  | restore
  v
active/restored
```

Administrative GET/list endpoints commonly support:

```text
include_deleted=true
```

for users with the required permission.

Public endpoints exclude soft-deleted records.

---

# 36. Request Schema Families

The OpenAPI contract currently exposes 127 schemas.

Important request families include:

## Authentication

```text
LoginRequest
RefreshRequest
LogoutRequest
```

## Account lifecycle

```text
RegisterRequest
VerifyEmailRequest
ResendVerificationRequest
ForgotPasswordRequest
ResetPasswordRequest
```

## Contact

```text
ContactInquiryPublicCreate
ContactInquiryUpdate
ContactInquiryReadUpdate
ContactInquiryStatusUpdate
ContactInquiryDeleteRequest
ContactInquiryRestoreRequest
```

## Profile

```text
ProfileCreate
ProfileUpdate
ProfileVisibilityUpdate
ProfileDeleteRequest
ProfileRestoreRequest
```

## Projects

```text
ProjectCreate
ProjectUpdate
ProjectStatusUpdate
ProjectVisibilityUpdate
ProjectFeaturedUpdate
ProjectDeleteRequest
ProjectRestoreRequest
```

## Categories

```text
ProjectCategoryCreate
ProjectCategoryUpdate
ProjectCategoryStatusUpdate
ProjectCategoryDeleteRequest
ProjectCategoryRestoreRequest
```

## Technologies

```text
ProjectTechnologyCreate
ProjectTechnologyUpdate
ProjectTechnologyStatusUpdate
ProjectTechnologyDeleteRequest
ProjectTechnologyRestoreRequest
```

## Project links

```text
ProjectLinkCreate
ProjectLinkUpdate
ProjectLinkStatusUpdate
ProjectLinkDeleteRequest
ProjectLinkRestoreRequest
```

## Project media

```text
ProjectMediaCreate
ProjectMediaUpdate
ProjectMediaPrimaryUpdate
ProjectMediaDeleteRequest
ProjectMediaRestoreRequest
```

## Experience

```text
ExperienceCreate
ExperienceUpdate
ExperienceVisibilityUpdate
ExperienceFeaturedUpdate
ExperienceDeleteRequest
ExperienceRestoreRequest
```

## Users

```text
AdminUserStatusUpdate
AdminUserDeleteRequest
AdminUserRestoreRequest
```

## RBAC

```text
RoleCreate
RoleUpdate
RolePermissionUpdate
UserRoleUpdate
```

---

# 37. Response Schema Families

Important response schemas include:

## Health

```text
HealthResponse
ReadinessResponse
ReadinessDependencies
```

## Authentication

```text
LoginResponse
RefreshResponse
TokenPair
UserRead
```

## Account lifecycle

```text
RegisterResponse
RegisteredUserResponse
VerifyEmailResponse
ResendVerificationResponse
ForgotPasswordResponse
ResetPasswordResponse
```

## Contact

```text
ContactInquiryPublicResponse
ContactInquirySummary
ContactInquiryAdminRead
ContactInquiryAssigneeOption
ContactInquiryProjectOption
```

## Portfolio

```text
ProjectRead
ProjectSummary
ProjectAdminRead

ProjectCategoryRead
ProjectCategorySummary
ProjectCategoryAdminRead

ProjectTechnologyRead
ProjectTechnologySummary
ProjectTechnologyAdminRead

ProjectLinkRead
ProjectLinkAdminRead

ProjectMediaRead
ProjectMediaAdminRead

ProfileRead
ProfileAdminRead

ExperienceRead
ExperienceSummary
ExperienceAdminRead
```

## User administration

```text
AdminUserSummary
AdminUserDetail
AdminUserListResponse
```

## RBAC

```text
RoleRead
PermissionRead
```

---

# 38. Enumerations

The API schema includes controlled enum values for several domains.

Examples include:

```text
ProjectStatus
ProjectVisibility
ProjectTechnologyCategory
ProjectMediaType
ProjectLinkType

ProfileAvailabilityStatus

EmploymentType
ExperienceLocationType

ContactInquiryType
ContactInquiryStatus
ContactInquiryPriority

UserStatus
UserSortField
SortDirection
```

Clients should use API-defined enum values rather than inventing display text as API values.

---

# 39. Project Status

Current project lifecycle schema includes:

```text
draft
published
archived
```

A published project must also satisfy the database publication timestamp invariant.

Public access additionally requires public visibility and non-deleted state.

---

# 40. Project Visibility

Current project visibility states include:

```text
public
private
unlisted
```

The public project API exposes only records eligible for public access.

---

# 41. Experience Filters

Experience APIs use controlled values for:

```text
employment_type
location_type
```

Administration also supports filters such as:

```text
is_current
is_public
is_featured
include_deleted
```

Public filters intentionally do not expose private/deleted visibility controls.

---

# 42. Contact Inquiry Workflow

Contact inquiry states include:

```text
new
in_progress
responded
closed
spam
```

Priority includes:

```text
low
normal
high
urgent
```

Administrative APIs can modify:

```text
workflow status
read state
priority
assignment
internal notes
inquiry type
```

according to schema and service validation.

---

# 43. UUID Identifiers

Administrative resources generally use UUID identifiers.

Examples:

```text
{project_id}
{category_id}
{technology_id}
{media_id}
{link_id}
{experience_id}
{inquiry_id}
{user_id}
{role_id}
```

Malformed UUID values normally result in request validation failure.

---

# 44. Public Slugs

Public portfolio resources generally use human-readable slugs rather than UUIDs.

Examples:

```text
/portfolio/projects/{slug}
/portfolio/categories/{slug}
/portfolio/technologies/{slug}
/portfolio/experiences/{slug}
```

This keeps public portfolio URLs stable and presentation-friendly while administration continues to use immutable database IDs.

---

# 45. Search

Administrative and public list APIs support domain-specific search.

Search terms generally have validation such as:

```text
minimum length: 1
maximum length: 200
```

Search behavior is implemented by the relevant service/repository and can span multiple domain fields.

Do not assume every search endpoint searches exactly the same columns.

---

# 46. Sorting

Administrative list APIs commonly provide:

```text
sort_by
sort_direction
```

Typical direction:

```text
asc
desc
```

Allowed `sort_by` values differ by domain.

Clients should not send arbitrary database-column names.

---

# 47. `include_deleted`

The administrative flag:

```text
include_deleted
```

does not bypass authorization.

A request must first have the appropriate read/manage permission.

It only changes whether otherwise-authorized administrative queries may include soft-deleted records.

Public APIs do not expose this control.

---

# 48. Next.js BFF Boundary

The API documented here is the FastAPI contract.

The frontend also exposes Next.js application/BFF routes such as:

```text
/api/admin-auth/login
/api/admin-auth/logout
/api/admin-auth/refresh
/api/admin-auth/session

/api/admin/...
```

These are **not** FastAPI `/api/v1` operations and therefore are not included in the FastAPI OpenAPI contract.

Production Nginx routing preserves this distinction:

```text
/api/v1/*      -> FastAPI
everything else -> Next.js
```

The frontend admin BFF stores backend credentials in HttpOnly cookies and proxies protected operations server-side.

See:

```text
docs/architecture/frontend-architecture.md
docs/security/authentication.md
```

---

# 49. Public Browser API vs Server API

In production:

```text
browser-visible FastAPI:
https://<domain>/api/v1
```

Next.js server/BFF uses:

```text
http://backend:8000/api/v1
```

inside the Docker network.

The internal address is configured through:

```text
BACKEND_API_URL
```

and must not be exposed as a browser secret/configuration dependency.

---

# 50. Contact Submission Privacy

The public contact endpoint derives the directly connected request IP from the request connection.

Trusted reverse-proxy forwarding behavior must be controlled by trusted deployment infrastructure rather than blindly trusting arbitrary forwarding headers from untrusted clients.

The contact service uses privacy-preserving hashing/fingerprinting rather than requiring raw client IP storage in the inquiry data model.

---

# 51. Endpoint Count by Domain

Current operation inventory:

```text
Root                                      1
Health                                    3
Authentication                            5
Account lifecycle                         5
Public contact                            1
Public portfolio                         11
Admin contact inquiries                  10
Admin portfolio categories               7
Admin portfolio technologies             7
Admin portfolio projects/links/media     23
Admin portfolio profile                   6
Admin portfolio experience                8
Admin users                                5
RBAC                                       7
                                         --
Total                                     99
```

These operations are distributed across:

```text
73 OpenAPI paths
```

because multiple HTTP methods can share one path.

---

# 52. OpenAPI Security Interpretation

An OpenAPI entry such as:

```text
security:
  - HTTPBearer: []
```

means bearer authentication is required.

OpenAPI does not, by itself, communicate the application's full RBAC permission requirement.

For example:

```text
GET /api/v1/admin/portfolio/projects
```

shows HTTP Bearer security in OpenAPI, while the endpoint implementation additionally requires:

```text
projects.read
```

Therefore API consumers and maintainers must treat:

```text
OpenAPI authentication metadata
+
FastAPI authorization dependency
```

as the complete protected-operation contract.

---

# 53. API Contract Validation

From:

```text
backend/
```

the current OpenAPI contract can be inspected without starting an external HTTP server:

```powershell
@'
from app.main import app

schema = app.openapi()

print(schema["info"]["title"])
print(schema["info"]["version"])
print(len(schema["paths"]))
print(len(schema["components"]["schemas"]))
'@ | uv run python -
```

Current expected values:

```text
Akahalu Portfolio API
1.0.0
73
127
```

---

# 54. Verify Security Scheme

From `backend/`:

```powershell
@'
from pprint import pprint
from app.main import app

schema = app.openapi()

pprint(
    schema
    .get("components", {})
    .get("securitySchemes", {})
)
'@ | uv run python -
```

Expected:

```text
HTTPBearer
type=http
scheme=bearer
```

---

# 55. Production Verification

When the production stack is running, verify public API health through Nginx:

```text
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

and verify production documentation suppression:

```text
GET /docs         -> 404
GET /openapi.json -> 404
```

Do not enable public API documentation simply to debug a production deployment.

Use controlled logs, health endpoints, and internal inspection instead.

---

# 56. API Change Rules

Future API changes should follow these rules:

1. Keep normal backend routes under the versioned `/api/v1` boundary.
2. Use explicit Pydantic request and response schemas.
3. Protect administrative routes with backend authentication.
4. Protect administrative capabilities with explicit permissions.
5. Never rely on frontend visibility as API authorization.
6. Keep public and administrative visibility rules separate.
7. Maintain soft-deletion semantics consistently.
8. Use UUIDs for administrative resource identity where established.
9. Preserve stable public slug semantics.
10. Add/update integration tests whenever endpoint behavior changes.
11. Update identity bootstrap when new permission literals are introduced.
12. Update frontend TypeScript contracts when API response contracts change.
13. Update this API reference when routes or schemas change.
14. Review lifecycle-token exposure before final public self-service launch.
15. Preserve production API-documentation policy unless there is an explicit security-reviewed reason to change it.

---

# 57. Related Documentation

See:

```text
docs/architecture/system-overview.md
docs/architecture/backend-architecture.md
docs/architecture/frontend-architecture.md

docs/database/data-model.md
docs/database/migrations.md

docs/security/authentication.md
docs/security/authorization.md

docs/deployment/deployment-readiness.md
docs/deployment/environment-variables.md
docs/deployment/production-runbook.md
```
