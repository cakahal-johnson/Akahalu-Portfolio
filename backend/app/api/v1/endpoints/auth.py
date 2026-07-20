from typing import Annotated, NoReturn

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import CurrentUser
from app.db.dependencies import get_db_session
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
)
from app.schemas.user import UserRead
from app.services.authentication_service import (
    AuthenticationError,
    authentication_service,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def raise_authentication_error(
    exception: AuthenticationError,
) -> NoReturn:
    raise HTTPException(
        status_code=exception.status_code,
        detail={
            "code": exception.error_code,
            "message": exception.message,
        },
    ) from exception


def get_request_ip_address(
    request: Request,
) -> str | None:
    if request.client is None:
        return None

    return request.client.host


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    request: Request,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> LoginResponse:
    try:
        result = await authentication_service.login(
            database_session,
            email=str(payload.email),
            password=payload.password.get_secret_value(),
            ip_address=get_request_ip_address(request),
            user_agent=request.headers.get("user-agent"),
            device_name=payload.device_name,
        )
    except AuthenticationError as exc:
        raise_authentication_error(exc)

    return LoginResponse(
        user=UserRead.model_validate(result.user),
        tokens=result.tokens,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    payload: RefreshRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RefreshResponse:
    try:
        result = await authentication_service.refresh(
            database_session,
            raw_refresh_token=(payload.refresh_token.get_secret_value()),
        )
    except AuthenticationError as exc:
        raise_authentication_error(exc)

    return RefreshResponse(
        user=UserRead.model_validate(result.user),
        tokens=result.tokens,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    payload: LogoutRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> Response:
    if payload.refresh_token is not None:
        await authentication_service.logout(
            database_session,
            raw_refresh_token=(payload.refresh_token.get_secret_value()),
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_all(
    current_user: CurrentUser,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> Response:
    await authentication_service.logout_all(
        database_session,
        user_id=current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: CurrentUser,
) -> UserRead:
    return UserRead.model_validate(current_user)
