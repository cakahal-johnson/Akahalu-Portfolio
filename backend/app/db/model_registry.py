from app.db.base import Base

# Import all model modules so SQLAlchemy registers their tables
# with Base.metadata before Alembic performs autogeneration.
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


__all__ = [
    "Base",
    "Permission",
    "Role",
    "User",
]
