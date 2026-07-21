from app.db.base import Base

# Association tables
from app.models.associations import (
    role_permissions,
    user_roles,
)

# Identity & Security
from app.models.email_verification_token import EmailVerificationToken
from app.models.login_attempt import LoginAttempt
from app.models.password_reset_token import PasswordResetToken
from app.models.permission import Permission
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.session import Session
from app.models.user import User

# Portfolio
from app.models.project import Project
from app.models.project_associations import (
    ProjectTechnologyAssociation,
)
from app.models.project_category import ProjectCategory
from app.models.project_link import ProjectLink
from app.models.project_media import ProjectMedia
from app.models.project_technology import ProjectTechnology


__all__ = [
    "Base",
    # Association tables
    "role_permissions",
    "user_roles",
    # Identity
    "EmailVerificationToken",
    "LoginAttempt",
    "PasswordResetToken",
    "Permission",
    "RefreshToken",
    "Role",
    "Session",
    "User",
    # Portfolio
    "Project",
    "ProjectCategory",
    "ProjectTechnology",
    "ProjectTechnologyAssociation",
    "ProjectMedia",
    "ProjectLink",
]
