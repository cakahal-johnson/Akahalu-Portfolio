from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.schemas.account_lifecycle import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    RegisterRequest,
    RegisterResponse,
    RegisteredUserResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.services.account_lifecycle_service import (
    AccountLifecycleError,
    AccountLifecycleService,
    EmailAlreadyRegisteredError,
    InactiveAccountError,
    InvalidPasswordResetTokenError,
    InvalidVerificationTokenError,
)


router = APIRouter(
    prefix="/account",
    tags=["Account lifecycle"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_account(
    payload: RegisterRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RegisterResponse:
    service = AccountLifecycleService(database_session)

    try:
        result = await service.register(
            email=str(payload.email),
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            display_name=payload.display_name,
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "email_already_registered",
                "message": str(exc),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "invalid_registration",
                "message": str(exc),
            },
        ) from exc

    return RegisterResponse(
        user=RegisteredUserResponse.model_validate(result.user),
        message="Registration completed. Please verify your email address.",
        verification_token=result.verification_token,
        verification_token_expires_at=(result.verification_token_expires_at),
    )


@router.post(
    "/verify-email",
    response_model=VerifyEmailResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    payload: VerifyEmailRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> VerifyEmailResponse:
    service = AccountLifecycleService(database_session)

    try:
        result = await service.verify_email(
            raw_token=payload.token,
        )
    except InvalidVerificationTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_verification_token",
                "message": str(exc),
            },
        ) from exc
    except InactiveAccountError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "inactive_account",
                "message": str(exc),
            },
        ) from exc

    return VerifyEmailResponse(
        user=RegisteredUserResponse.model_validate(result.user),
        message="Email address verified successfully.",
    )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse,
    status_code=status.HTTP_200_OK,
)
async def resend_verification_email(
    payload: ResendVerificationRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> ResendVerificationResponse:
    service = AccountLifecycleService(database_session)

    user = await service.get_user_by_email(str(payload.email))

    generic_message = (
        "If an eligible account exists, a verification email will be sent."
    )

    if user is None:
        return ResendVerificationResponse(
            message=generic_message,
        )

    try:
        token = await service.create_email_verification_token(user=user)
    except AccountLifecycleError:
        return ResendVerificationResponse(
            message=generic_message,
        )

    return ResendVerificationResponse(
        message=generic_message,
        verification_token=token.raw_token,
        verification_token_expires_at=token.expires_at,
    )


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> ForgotPasswordResponse:
    service = AccountLifecycleService(database_session)

    generic_message = (
        "If an eligible account exists, password reset instructions will be sent."
    )

    result = await service.request_password_reset(
        email=str(payload.email),
    )

    if result is None:
        return ForgotPasswordResponse(
            message=generic_message,
        )

    return ForgotPasswordResponse(
        message=generic_message,
        reset_token=result.reset_token,
        reset_token_expires_at=result.reset_token_expires_at,
    )


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    payload: ResetPasswordRequest,
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> ResetPasswordResponse:
    service = AccountLifecycleService(database_session)

    try:
        await service.reset_password(
            raw_token=payload.token,
            new_password=payload.new_password,
        )
    except InvalidPasswordResetTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_password_reset_token",
                "message": str(exc),
            },
        ) from exc
    except InactiveAccountError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "inactive_account",
                "message": str(exc),
            },
        ) from exc

    return ResetPasswordResponse(
        message="Password reset successfully.",
    )
