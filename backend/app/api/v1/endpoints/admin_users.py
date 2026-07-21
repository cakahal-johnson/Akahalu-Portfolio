from typing import Annotated, NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.db.dependencies import get_db_session
from app.models.user import User
from app.schemas.user_admin import (
    AdminUserDeleteRequest,
    AdminUserDetail,
    AdminUserListQuery,
    AdminUserListResponse,
    AdminUserRestoreRequest,
    AdminUserStatusUpdate,
)
from app.services.user_admin_service import (
    UserAdminError,
    user_admin_service,
)


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
)


UserManager = Annotated[
    User,
    Depends(
        require_permission(
            "users.manage",
        )
    ),
]

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


def raise_user_admin_error(
    exception: UserAdminError,
) -> NoReturn:
    raise HTTPException(
        status_code=exception.status_code,
        detail={
            "code": exception.error_code,
            "message": exception.message,
        },
    ) from exception


@router.get(
    "",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_users(
    _: UserManager,
    database_session: DatabaseSession,
    query: Annotated[
        AdminUserListQuery,
        Query(),
    ],
) -> AdminUserListResponse:
    return await user_admin_service.list_users(
        database_session,
        query=query,
    )


@router.get(
    "/{user_id}",
    response_model=AdminUserDetail,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: UUID,
    _: UserManager,
    database_session: DatabaseSession,
    include_deleted: Annotated[
        bool,
        Query(
            description="Allow retrieval of a soft-deleted user account.",
        ),
    ] = False,
) -> AdminUserDetail:
    try:
        return await user_admin_service.get_user(
            database_session,
            user_id=user_id,
            include_deleted=include_deleted,
        )
    except UserAdminError as exc:
        raise_user_admin_error(exc)


@router.patch(
    "/{user_id}/status",
    response_model=AdminUserDetail,
    status_code=status.HTTP_200_OK,
)
async def update_user_status(
    user_id: UUID,
    payload: AdminUserStatusUpdate,
    current_user: UserManager,
    database_session: DatabaseSession,
) -> AdminUserDetail:
    try:
        return await user_admin_service.update_status(
            database_session,
            actor_user_id=current_user.id,
            user_id=user_id,
            payload=payload,
        )
    except UserAdminError as exc:
        raise_user_admin_error(exc)


@router.delete(
    "/{user_id}",
    response_model=AdminUserDetail,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: UUID,
    payload: AdminUserDeleteRequest,
    current_user: UserManager,
    database_session: DatabaseSession,
) -> AdminUserDetail:
    try:
        return await user_admin_service.delete_user(
            database_session,
            actor_user_id=current_user.id,
            user_id=user_id,
            payload=payload,
        )
    except UserAdminError as exc:
        raise_user_admin_error(exc)


@router.post(
    "/{user_id}/restore",
    response_model=AdminUserDetail,
    status_code=status.HTTP_200_OK,
)
async def restore_user(
    user_id: UUID,
    payload: AdminUserRestoreRequest,
    _: UserManager,
    database_session: DatabaseSession,
) -> AdminUserDetail:
    try:
        return await user_admin_service.restore_user(
            database_session,
            user_id=user_id,
            payload=payload,
        )
    except UserAdminError as exc:
        raise_user_admin_error(exc)
