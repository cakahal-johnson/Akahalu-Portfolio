from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.db.dependencies import get_db_session
from app.models.user import User
from app.schemas.permission import PermissionRead
from app.schemas.role import RoleRead
from app.services.rbac_service import rbac_service


router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
)


RoleManager = Annotated[
    User,
    Depends(
        require_permission(
            "roles.manage",
        )
    ),
]


@router.get(
    "/roles",
    response_model=list[RoleRead],
    status_code=status.HTTP_200_OK,
)
async def list_roles(
    _: RoleManager,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> list[RoleRead]:
    roles = await rbac_service.list_roles(
        database_session,
    )

    return [RoleRead.model_validate(role) for role in roles]


@router.get(
    "/permissions",
    response_model=list[PermissionRead],
    status_code=status.HTTP_200_OK,
)
async def list_permissions(
    _: RoleManager,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> list[PermissionRead]:
    permissions = await rbac_service.list_permissions(
        database_session,
    )

    return [PermissionRead.model_validate(permission) for permission in permissions]
