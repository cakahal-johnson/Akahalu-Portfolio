# backend/app/api/dependencies/__init__.py

from app.api.dependencies.authentication import (
    CurrentUser,
    authentication_exception,
    get_current_user,
)
from app.api.dependencies.authorization import (
    AuthorizationDependency,
    authorization_exception,
    get_active_permission_codes,
    get_active_role_names,
    require_any_permission,
    require_any_role,
    require_permission,
    require_role,
    user_has_any_permission,
    user_has_any_role,
    user_has_permission,
    user_has_role,
)


__all__ = [
    "AuthorizationDependency",
    "CurrentUser",
    "authentication_exception",
    "authorization_exception",
    "get_active_permission_codes",
    "get_active_role_names",
    "get_current_user",
    "require_any_permission",
    "require_any_role",
    "require_permission",
    "require_role",
    "user_has_any_permission",
    "user_has_any_role",
    "user_has_permission",
    "user_has_role",
]
