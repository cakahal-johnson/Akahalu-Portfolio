from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.db.dependencies import get_db_session
from app.models.user import User
from app.schemas.permission import PermissionRead
from app.schemas.role import (
    RoleCreate,
    RolePermissionUpdate,
    RoleRead,
    RoleUpdate,
)
from app.services.rbac_service import (
    RbacError,
    rbac_service,
)


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


def raise_rbac_error(
    exception: RbacError,
) -> None:
    raise HTTPException(
        status_code=exception.status_code,
        detail={
            "code": exception.error_code,
            "message": exception.message,
        },
    ) from exception


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


@router.post(
    "/roles",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    payload: RoleCreate,
    _: RoleManager,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RoleRead:
    try:
        role = await rbac_service.create_role(
            database_session,
            payload=payload,
        )
    except RbacError as exc:
        raise_rbac_error(exc)

    return RoleRead.model_validate(role)


@router.patch(
    "/roles/{role_id}",
    response_model=RoleRead,
    status_code=status.HTTP_200_OK,
)
async def update_role(
    role_id: UUID,
    payload: RoleUpdate,
    _: RoleManager,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RoleRead:
    try:
        role = await rbac_service.update_role(
            database_session,
            role_id=role_id,
            payload=payload,
        )
    except RbacError as exc:
        raise_rbac_error(exc)

    return RoleRead.model_validate(role)


@router.put(
    "/roles/{role_id}/permissions",
    response_model=RoleRead,
    status_code=status.HTTP_200_OK,
)
async def replace_role_permissions(
    role_id: UUID,
    payload: RolePermissionUpdate,
    _: RoleManager,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RoleRead:
    try:
        role = await rbac_service.replace_role_permissions(
            database_session,
            role_id=role_id,
            payload=payload,
        )
    except RbacError as exc:
        raise_rbac_error(exc)

    return RoleRead.model_validate(role)


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
