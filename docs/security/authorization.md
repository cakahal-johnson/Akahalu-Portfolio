# Authorization

## 1. Purpose

This document describes the authorization model used by Akahalu Portfolio.

Authorization determines what an already authenticated identity may do.

The backend uses role-based access control (RBAC) built around:

```text
users
roles
permissions
user_roles
role_permissions
```

FastAPI is the authoritative authorization boundary.

Frontend permission checks are used to improve navigation and user experience, but they must never be treated as sufficient protection for API operations.

Authentication is documented separately in:

```text
docs/security/authentication.md
```

---

## 2. Authorization Architecture

The authorization flow is:

```text
request
   |
   v
authenticate user
   |
   v
validate session
   |
   v
load user roles + permissions
   |
   v
discard inactive/deleted roles
   |
   v
discard inactive/deleted permissions
   |
   v
superuser?
   |           |
  yes         no
   |           |
 allow     required permission?
               |          |
              yes        no
               |          |
             allow       403
```

Authentication always precedes protected authorization checks.

An unauthenticated request must not be turned into a permission failure.

---

## 3. Core Authorization Components

The primary authorization implementation is located in:

```text
backend/app/api/dependencies/authentication.py
backend/app/api/dependencies/authorization.py
backend/app/api/v1/endpoints/rbac.py
backend/app/services/rbac_service.py
backend/app/services/identity_service.py
backend/app/models/user.py
backend/app/models/role.py
backend/app/models/permission.py
backend/app/models/associations.py
backend/app/repositories/user_repository.py
backend/app/repositories/role_repository.py
backend/app/repositories/permission_repository.py
backend/scripts/seed_identity.py
```

Administrative domain routers use these authorization dependencies to enforce their own permission requirements.

---

## 4. RBAC Data Model

The authorization model is many-to-many at both levels.

```text
User
 |
 | many-to-many
 v
Role
 |
 | many-to-many
 v
Permission
```

The association tables are:

```text
user_roles
role_permissions
```

Conceptually:

```text
users
  |
  +---- user_roles ---- roles
                         |
                         +---- role_permissions ---- permissions
```

A user may have multiple roles.

A role may belong to multiple users.

A role may contain multiple permissions.

A permission may belong to multiple roles.

Effective permissions are the union of valid permissions contributed by all valid roles assigned to the user.

---

## 5. User Authorization State

The `User` model includes:

```text
is_active
is_verified
is_superuser
deleted_at
roles
```

Authentication prevents inactive or deleted users from using protected sessions.

For backend RBAC permission checks, the most important authorization attributes are:

```text
is_superuser
roles
```

A user's roles are evaluated dynamically from the persisted RBAC relationships loaded for the authenticated session.

---

## 6. Active Roles Only

A role contributes authorization only when:

```text
role.is_active == true
role.deleted_at == null
```

Inactive roles are ignored.

Soft-deleted roles are ignored.

Role names are normalized by trimming and converting to lowercase before comparison.

Therefore a role record remaining in the database does not automatically continue to grant access after it has been disabled or deleted.

---

## 7. Active Permissions Only

A permission contributes authorization only when:

```text
permission.is_active == true
permission.deleted_at == null
```

Permissions connected to inactive or deleted roles do not contribute access.

Inactive permissions are also ignored even when they remain assigned to an otherwise active role.

Permission codes are normalized by trimming and lowercasing before comparison.

---

## 8. Superuser Bypass

The `User` model contains:

```text
is_superuser
```

When:

```text
is_superuser == true
```

the backend role and permission helper functions treat the user as authorized regardless of explicit role/permission assignments.

The bypass applies to:

```text
user_has_role
user_has_any_role
user_has_permission
user_has_any_permission
```

This is intentional and is covered by integration tests across administrative domains.

A superuser is still subject to authentication and account-state requirements.

`is_superuser` does not permit an inactive, deleted, or otherwise invalid authentication session to bypass authentication.

---

## 9. Authorization Dependencies

The reusable authorization module provides:

```text
require_role(...)
require_any_role(...)
require_permission(...)
require_any_permission(...)
```

These functions return FastAPI dependencies.

A protected endpoint can therefore declare its authorization requirement directly at the API boundary.

Conceptually:

```python
Depends(require_permission("projects.update"))
```

means:

```text
authenticate request
      |
      v
resolve current user
      |
      v
superuser?
  |          |
 yes        no
  |          |
allow   has projects.update?
             |       |
            yes     no
             |       |
           allow    403
```

---

## 10. Authentication vs Authorization Responses

Missing or invalid authentication returns HTTP `401`.

Examples include:

```text
missing bearer credentials
invalid access token
expired access token
invalid authentication session
revoked authentication session
```

A validly authenticated user who lacks required authority receives HTTP `403`.

The normal permission-denial code is:

```text
insufficient_permissions
```

Role requirements can use:

```text
role_required
```

This distinction makes security behavior easier to reason about:

```text
401 = identity/session cannot be accepted
403 = identity is accepted but action is not authorized
```

---

## 11. Canonical Permission Set

The identity bootstrap currently synchronizes exactly 17 application permissions.

### Portfolio projects

```text
projects.read
projects.create
projects.update
projects.delete
```

These permissions cover the projects domain and its associated administration features such as:

```text
projects
project categories
technologies
project links
project media
project visibility
project lifecycle state
featured state
```

### Portfolio profile

```text
profile.read
profile.create
profile.update
profile.delete
```

### Professional experience

```text
experience.read
experience.create
experience.update
experience.delete
```

### Contact inquiries

```text
contact_inquiries.read
contact_inquiries.update
contact_inquiries.delete
```

### User administration

```text
users.manage
```

### RBAC administration

```text
roles.manage
```

These permission codes are the canonical current authorization vocabulary.

Do not reintroduce obsolete permission names such as earlier experimental:

```text
users.read
messages.read
messages.manage
blog.*
settings.manage
```

unless a future feature intentionally adds them to the current synchronized permission model.

---

## 12. System Roles

The identity bootstrap synchronizes four system roles:

```text
super_admin
admin
editor
viewer
```

They are created as system roles and their permissions are synchronized from the current permission constants.

This is preferable to relying on manual database setup because deployment can restore the intended baseline authorization model deterministically.

---

## 13. Super Administrator Role

Role:

```text
super_admin
```

Display name:

```text
Super Administrator
```

The role is synchronized with all 17 current permissions.

Its intended role-level access is:

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

The user-level:

```text
is_superuser
```

flag also independently provides the backend superuser bypass.

The role and the user flag are related administrative concepts but should not be confused as the same mechanism.

---

## 14. Administrator Role

Role:

```text
admin
```

The administrator role receives every synchronized application permission except:

```text
roles.manage
```

Therefore it receives 16 current permissions.

Its purpose is full operational administration without authority to modify the RBAC system itself.

This separation protects role and permission administration as a more privileged capability.

---

## 15. Content Editor Role

Role:

```text
editor
```

The editor receives the following 10 permissions:

```text
projects.read
projects.create
projects.update
projects.delete

profile.read
profile.update

experience.read
experience.create
experience.update
experience.delete
```

Notably, the editor does **not** receive:

```text
profile.create
profile.delete

contact_inquiries.*
users.manage
roles.manage
```

The role is intended to manage normal portfolio content without access to user administration, inquiries, or RBAC administration.

---

## 16. Viewer Role

Role:

```text
viewer
```

The bootstrap derives viewer permissions from current permission codes ending in:

```text
.read
```

With the current 17-permission set, this produces:

```text
projects.read
profile.read
experience.read
contact_inquiries.read
```

The viewer therefore has read-only administrative access to current readable administrative domains.

Because the rule is based on `*.read`, future additions to the permission set should be reviewed carefully: a newly added permission ending in `.read` may automatically become part of the synchronized viewer role.

---

## 17. Current System Role Matrix

| Permission                 | super_admin | admin | editor | viewer |
| -------------------------- | ----------: | ----: | -----: | -----: |
| `projects.read`            |           ✓ |     ✓ |      ✓ |      ✓ |
| `projects.create`          |           ✓ |     ✓ |      ✓ |      — |
| `projects.update`          |           ✓ |     ✓ |      ✓ |      — |
| `projects.delete`          |           ✓ |     ✓ |      ✓ |      — |
| `profile.read`             |           ✓ |     ✓ |      ✓ |      ✓ |
| `profile.create`           |           ✓ |     ✓ |      — |      — |
| `profile.update`           |           ✓ |     ✓ |      ✓ |      — |
| `profile.delete`           |           ✓ |     ✓ |      — |      — |
| `experience.read`          |           ✓ |     ✓ |      ✓ |      ✓ |
| `experience.create`        |           ✓ |     ✓ |      ✓ |      — |
| `experience.update`        |           ✓ |     ✓ |      ✓ |      — |
| `experience.delete`        |           ✓ |     ✓ |      ✓ |      — |
| `contact_inquiries.read`   |           ✓ |     ✓ |      — |      ✓ |
| `contact_inquiries.update` |           ✓ |     ✓ |      — |      — |
| `contact_inquiries.delete` |           ✓ |     ✓ |      — |      — |
| `users.manage`             |           ✓ |     ✓ |      — |      — |
| `roles.manage`             |           ✓ |     — |      — |      — |

The `is_superuser` flag can bypass these permission assignments when the authenticated account is otherwise valid.

---

## 18. Portfolio Project Authorization

The projects permission family is shared by several related administrative entities.

### Read

```text
projects.read
```

protects read-oriented administration for:

```text
projects
categories
technologies
project links
project media
```

### Create

```text
projects.create
```

protects creation operations across the project-management domain.

### Update

```text
projects.update
```

protects editing and non-destructive lifecycle changes such as:

```text
content updates
project status changes
visibility changes
featured state
association changes
restoration operations where defined as update semantics
```

### Delete

```text
projects.delete
```

protects destructive or archival operations that the relevant router defines as delete authority.

Public portfolio project endpoints do not rely on administrator RBAC; instead they expose only content that satisfies the public publication rules.

---

## 19. Profile Authorization

Profile administration uses:

```text
profile.read
profile.create
profile.update
profile.delete
```

The public profile remains separate from the administrator API.

Public exposure depends on public-profile lifecycle state rather than administrator credentials.

Administration must remain permission-protected even when a corresponding record is publicly readable.

---

## 20. Experience Authorization

Professional experience administration uses:

```text
experience.read
experience.create
experience.update
experience.delete
```

Tests verify that:

* unauthenticated administrator requests are rejected;
* authenticated users lacking a required permission receive `403`;
* users with the appropriate permission can perform the operation;
* superusers can bypass explicit experience permission assignments.

Public experience endpoints independently hide private and soft-deleted experience records.

---

## 21. Contact Inquiry Authorization

Administrative inquiry access uses:

```text
contact_inquiries.read
contact_inquiries.update
contact_inquiries.delete
```

Read authority covers access to submitted inquiry data.

Update authority covers workflow modifications such as:

```text
status changes
read-state changes
priority
assignment
internal administration
restoration where defined by the router as an update operation
```

Delete authority protects destructive inquiry operations.

Public submission of a contact inquiry is intentionally separate from administrative inquiry access.

A public visitor does not receive administrative inquiry-reading permissions simply because they can submit a message.

---

## 22. User Administration Authorization

All current administrator user-management operations are protected by:

```text
users.manage
```

The router prefix is:

```text
/api/v1/admin/users
```

The permission governs operations including:

```text
listing users
viewing user detail
activating/deactivating accounts
soft-deleting accounts
restoring accounts
other supported user lifecycle administration
```

There is no separate current `users.read` permission in the canonical 17-permission bootstrap.

This is intentional: current user-administration access is represented by:

```text
users.manage
```

---

## 23. User-Administration Safety Controls

Possession of `users.manage` does not remove all account-lifecycle protections.

The user-administration service prevents a user manager from:

```text
deactivating their own account
deleting their own account
deactivating or deleting the last active administrator
changing status on an already deleted account before restoration
```

When an account is deactivated or deleted, its existing authentication access is revoked by invalidating refresh tokens and sessions.

The last-administrator protection recognizes an active administrator when the user is either:

```text
is_superuser == true
```

or has the active, non-deleted:

```text
super_admin
```

role.

This reduces the risk of accidentally removing the final account capable of recovering administrative control.

---

## 24. RBAC Administration

RBAC administration is protected by:

```text
roles.manage
```

The RBAC API supports operations for roles, permissions, and user-role assignments.

Protected operations include capabilities such as:

```text
list roles
create roles
update roles
replace role permissions
list permissions
list user roles
replace user roles
```

The relevant API family is:

```text
/api/v1/rbac/*
```

Users without `roles.manage` receive a permission failure.

Superusers can access these operations through the superuser bypass.

---

## 25. RBAC Administration Separation

`roles.manage` is deliberately excluded from the normal `admin` role.

Therefore:

```text
admin
```

can manage normal application operations and users but cannot modify the permission system itself.

This creates a privilege boundary between:

```text
operational administration
```

and:

```text
authorization-policy administration
```

RBAC changes can potentially grant broad authority, so this separation should be preserved.

---

## 26. Identity Bootstrap

The canonical baseline authorization state is maintained by:

```text
backend/scripts/seed_identity.py
```

The production bootstrap can run:

```text
python -m scripts.seed_identity --skip-admin
```

to synchronize permissions and system roles without interactively creating an administrator.

The script:

1. ensures each canonical permission exists;
2. synchronizes each permission's metadata;
3. creates or updates system roles;
4. assigns the current permission sets to those roles;
5. optionally creates or recovers the first super administrator;
6. commits the synchronized identity state.

A successful synchronization reports the number of synchronized permissions and the four system roles.

With the current application this is:

```text
17 permissions
super_admin
admin
editor
viewer
```

---

## 27. Why Identity Synchronization Matters

Authorization requirements are encoded in application routers.

For example:

```text
projects.read
profile.update
experience.delete
users.manage
roles.manage
```

must exist in the database for non-superuser RBAC to work correctly.

A deployment containing newer endpoint permission requirements but an outdated identity seed can therefore create authorization failures.

For this reason, production deployment performs identity synchronization after database migration and before the application becomes the normal serving backend.

The identity bootstrap should remain idempotent and safe to run against an already initialized database.

---

## 28. Authorization Source of Truth

The following order of authority applies:

```text
FastAPI authorization dependency
        >
persisted active roles/permissions
        >
Next.js UI permission filtering
        >
browser state
```

The browser must never be treated as authoritative.

A user can manually issue HTTP requests regardless of whether the interface hides a button.

Therefore:

```text
hidden button != authorization
hidden navigation link != authorization
disabled form != authorization
client-side role check != authorization
```

Only the backend permission decision protects the operation.

---

## 29. Frontend Permission Awareness

The administration interface may use the authenticated user's roles and permissions to improve the UI.

Examples include:

```text
showing navigation entries
hiding inaccessible actions
disabling unavailable controls
selecting appropriate administrator views
```

This is desirable because users should not be encouraged to interact with features they cannot access.

However, every protected mutation and protected administrative read must still be authorized by FastAPI.

Frontend checks are advisory UX controls.

Backend checks are security controls.

---

## 30. Administrative Navigation

Current administrative navigation corresponds to permissions such as:

```text
Profile       -> profile.read
Projects      -> projects.read
Categories    -> projects.read
Technologies  -> projects.read
Experience    -> experience.read
Inquiries     -> contact_inquiries.read
Users         -> users.manage
```

A superuser can see permission-protected navigation through the frontend superuser logic.

Navigation configuration should be kept aligned with backend authorization, but a navigation mismatch must never be resolved by weakening backend permissions.

If the frontend fails to display a feature that the backend permits, fix the frontend permission mapping.

Do not remove backend authorization merely to make the menu appear.

---

## 31. Administrator Eligibility vs Permission Authorization

The Next.js BFF has an administrator-eligibility check.

A user is eligible for the administration application when the account is valid and either:

```text
is_superuser == true
```

or:

```text
has at least one active non-deleted role
```

This check determines whether the user may enter the administrative application.

It does **not** grant all administrator capabilities.

For example, a `viewer` may pass administrator eligibility but still be unable to create, update, or delete portfolio content.

FastAPI evaluates the actual permission required by each operation.

Therefore:

```text
admin application eligibility
        !=
authorization for every admin action
```

---

## 32. BFF Authorization Boundary

The Next.js BFF forwards authenticated administrator requests to FastAPI.

It may:

```text
read authentication cookies
refresh authentication
attach the bearer access token
retry after successful refresh
relay FastAPI responses
```

It must not invent authorization.

The BFF must not convert a FastAPI `403` into a successful response.

Similarly, a frontend page must not bypass FastAPI by directly modifying protected data.

All protected data mutations terminate at an authorized FastAPI endpoint.

---

## 33. Soft-Deleted Authorization Objects

Roles and permissions inherit application lifecycle metadata including soft-deletion state.

The authorization dependency deliberately ignores:

```text
role.deleted_at != null
permission.deleted_at != null
```

This prevents a soft-deleted authorization object from continuing to grant access simply because historical association rows still exist.

The same principle applies to inactive objects.

This behavior is covered by authorization/RBAC tests.

---

## 34. Multiple Roles

A user may have more than one role.

Effective permission evaluation takes the union of active permissions from every active, non-deleted assigned role.

For example:

```text
Role A:
  projects.read

Role B:
  experience.update
```

produces effective permissions:

```text
projects.read
experience.update
```

No role ordering is required.

A permission granted by any eligible assigned role is sufficient for a normal `require_permission` check.

---

## 35. `require_any_permission`

Where a route legitimately permits more than one authority, the backend can use:

```text
require_any_permission(...)
```

The dependency authorizes the request when the user has at least one of the supplied permissions.

The same active/deleted filtering and superuser bypass rules apply.

This should be used only when the domain semantics genuinely permit alternatives.

It should not be used merely to work around an incorrectly assigned permission.

---

## 36. `require_role` and `require_any_role`

The backend also supports direct role requirements:

```text
require_role(...)
require_any_role(...)
```

Role authorization observes the same rules:

```text
inactive roles are ignored
deleted roles are ignored
names are normalized
superusers bypass the role requirement
```

Permission-based authorization should normally be preferred for business operations because it expresses capability rather than organizational label.

Direct role checks are appropriate when an operation is inherently tied to a role identity rather than a reusable capability.

---

## 37. Principle of Least Privilege

Authorization changes should follow least privilege.

A role should receive only the permissions needed for its intended responsibility.

The current system demonstrates this separation:

```text
viewer
  -> read-only administrative visibility

editor
  -> portfolio content management

admin
  -> broad operational administration

super_admin
  -> full system and RBAC administration
```

New permissions should not automatically be added to every role without evaluating whether each role actually needs them.

---

## 38. Permission Naming Convention

Current permission codes follow:

```text
domain.action
```

Examples:

```text
projects.read
profile.update
experience.delete
roles.manage
```

New permissions should preserve this convention.

Prefer stable business capabilities over route-specific names.

Good:

```text
certifications.read
certifications.create
certifications.update
certifications.delete
```

Avoid unnecessarily implementation-specific names such as:

```text
get_certification_endpoint
press_certification_button
certification_page_access
```

The permission name should remain meaningful even if routes or frontend structure later change.

---

## 39. Adding a New Protected Domain

When a new administrative domain is added, authorization work should include all of the following:

```text
define canonical permissions
add them to identity synchronization
map them intentionally to system roles
protect FastAPI routes
update frontend navigation/action visibility where appropriate
add migration/bootstrap compatibility where required
add integration tests
add authorization regression tests
update documentation
```

Do not implement only the frontend role check.

Do not implement only the database permission row.

The permission must be enforced at the API boundary.

---

## 40. Changing a Permission Code

Permission codes are application contracts.

Renaming:

```text
old.permission
```

to:

```text
new.permission
```

requires coordinated changes to:

```text
FastAPI route dependencies
identity bootstrap
existing database identity state
system role mappings
frontend permission checks
tests
documentation
```

A partial permission rename can cause either unexpected denial or accidental inconsistency.

Permission changes should therefore be reviewed similarly to API contract changes.

---

## 41. Role Assignment Changes

Changing a user's roles changes their effective authorization.

Role-assignment operations themselves are protected by:

```text
roles.manage
```

This avoids allowing a normal operational administrator to grant themselves or another account additional RBAC authority.

Role-assignment changes should continue to be performed server-side against persisted role records.

The browser must not be able to create an effective role assignment merely by modifying its local session representation.

---

## 42. Authorization and Existing Sessions

Role and permission data are loaded from the authenticated user's persisted authorization relationships as part of backend request handling.

The authorization decision therefore depends on current persisted role/permission state rather than a permission list encoded permanently inside the access JWT.

Access JWTs identify:

```text
user
session
token
```

but do not serve as the canonical role/permission store.

This is an important design property because permission changes do not require issuing a JWT containing a completely new permission claim set before backend RBAC can reflect database state.

---

## 43. Security Failure Examples

### Missing authentication

```text
GET protected endpoint
Authorization header absent
```

Result:

```text
401 invalid_authentication
```

### Valid user, missing permission

```text
authenticated user
required: experience.delete
effective permissions do not contain experience.delete
```

Result:

```text
403 insufficient_permissions
```

### Inactive role contains permission

```text
role.is_active = false
role.permissions includes projects.update
```

Result:

```text
projects.update is ignored
```

### Deleted permission

```text
permission.deleted_at != null
```

Result:

```text
permission does not contribute access
```

### Superuser without explicit permission row

```text
user.is_superuser = true
```

Result:

```text
permission check passes
```

provided authentication and account state remain valid.

---

## 44. Testing

Authorization behavior is covered by dedicated unit and integration tests including:

```text
backend/tests/unit/test_authorization.py
backend/tests/unit/test_identity_seed.py
backend/tests/integration/test_rbac_api.py
backend/tests/integration/test_admin_users_api.py
backend/tests/integration/test_admin_portfolio_categories_api.py
backend/tests/integration/test_admin_portfolio_technologies_api.py
backend/tests/integration/test_admin_portfolio_projects_api.py
backend/tests/integration/test_admin_portfolio_project_links_api.py
backend/tests/integration/test_admin_portfolio_project_media_api.py
backend/tests/integration/test_admin_portfolio_experiences_api.py
backend/tests/integration/test_contact_inquiries_api.py
backend/tests/integration/test_portfolio_profile_api.py
```

Authorization tests should continue to verify:

```text
unauthenticated requests -> 401
missing permission -> 403
correct permission -> success
superuser bypass -> success
inactive role -> no authority
deleted role -> no authority
inactive permission -> no authority
deleted permission -> no authority
role assignment behavior
identity bootstrap synchronization
account deactivation revokes access
account deletion revokes access
last-administrator protection
```

---

## 45. Identity-Seed Regression Protection

The identity bootstrap is part of the authorization contract.

Tests should ensure that permission literals actually required by application endpoints remain represented in the synchronized identity permission set.

This prevents a common deployment failure:

```text
endpoint starts requiring permission X
        |
        v
permission X missing from production identity bootstrap
        |
        v
every non-superuser receives 403
```

The identity bootstrap and endpoint permission requirements should evolve together.

---

## 46. Deployment

Production deployment synchronizes identity state after database migration.

The intended startup order is:

```text
PostgreSQL ready
      |
      v
Alembic migrations
      |
      v
identity bootstrap
      |
      v
FastAPI
      |
      v
Next.js / Nginx serving
```

The production bootstrap command uses:

```text
python -m scripts.seed_identity --skip-admin
```

The first administrator is not silently created from hard-coded production credentials.

Administrator creation/recovery is a deliberate administrative action.

---

## 47. Authorization Review Checklist

Before merging a change involving protected administration, verify:

```text
Does the endpoint require authentication?

What exact permission protects it?

Is that permission canonical?

Is it synchronized by seed_identity.py?

Which system roles should receive it?

Does FastAPI enforce it?

Does the frontend merely mirror rather than replace it?

Are inactive/deleted roles and permissions handled?

Does a superuser path remain tested?

Is denial tested?

Is success tested?

Does account deactivation/deletion revoke access when relevant?

Has the documentation been updated?
```

---

## 48. Rules for Future Authorization Changes

Future authorization work must preserve these rules:

1. FastAPI remains the authoritative authorization boundary.
2. Never remove backend permission enforcement just to make the frontend work.
3. Do not trust hidden buttons or navigation as security controls.
4. Keep permission codes centralized and synchronized.
5. Ignore inactive and deleted authorization objects.
6. Preserve explicit superuser semantics.
7. Keep `roles.manage` more privileged than normal operational administration.
8. Apply least privilege when changing system-role assignments.
9. Revoke authentication access when user lifecycle changes require it.
10. Protect role assignment itself with RBAC authority.
11. Test both allow and deny paths.
12. Update identity-bootstrap tests when endpoint permission requirements change.
13. Do not document obsolete permission codes as current capabilities.
14. Treat authorization changes as security-sensitive application contract changes.

---

## 49. Related Documentation

See:

```text
docs/security/authentication.md
docs/architecture/system-overview.md
docs/architecture/backend-architecture.md
docs/architecture/frontend-architecture.md
docs/database/data-model.md
docs/deployment/deployment-readiness.md
docs/deployment/production-runbook.md
```
