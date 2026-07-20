from app.db.base import Base

# Import every model so SQLAlchemy registers its table with
# Base.metadata before Alembic inspects the metadata.
from app.models.email_verification_token import EmailVerificationToken
from app.models.login_attempt import LoginAttempt
from app.models.password_reset_token import PasswordResetToken
from app.models.permission import Permission
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.session import Session
from app.models.user import User


__all__ = [
    "Base",
    "EmailVerificationToken",
    "LoginAttempt",
    "PasswordResetToken",
    "Permission",
    "RefreshToken",
    "Role",
    "Session",
    "User",
]
