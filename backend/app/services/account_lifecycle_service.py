from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.email_verification_token import (
    EmailVerificationToken,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.repositories.email_verification_token_repository import (
    EmailVerificationTokenRepository,
)
from app.repositories.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from app.repositories.refresh_token_repository import (
    refresh_token_repository,
)
from app.repositories.session_repository import (
    session_repository,
)
from app.security.account_tokens import (
    AccountToken,
    digest_account_token,
    generate_account_token,
    utc_now,
)
from app.security.passwords import hash_password


class AccountLifecycleError(Exception):
    """Base exception for account lifecycle operations."""


class EmailAlreadyRegisteredError(AccountLifecycleError):
    """Raised when registration uses an existing email address."""


class InvalidVerificationTokenError(AccountLifecycleError):
    """Raised when an email-verification token is invalid."""


class InvalidPasswordResetTokenError(AccountLifecycleError):
    """Raised when a password-reset token is invalid."""


class InactiveAccountError(AccountLifecycleError):
    """Raised when an operation targets an inactive account."""


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    user: User
    verification_token: str
    verification_token_expires_at: datetime


@dataclass(frozen=True, slots=True)
class EmailVerificationResult:
    user: User
    token: EmailVerificationToken


@dataclass(frozen=True, slots=True)
class PasswordResetRequestResult:
    reset_token: str
    reset_token_expires_at: datetime


@dataclass(frozen=True, slots=True)
class PasswordResetResult:
    user: User
    token: PasswordResetToken


class AccountLifecycleService:
    def __init__(
        self,
        database_session: AsyncSession,
        *,
        email_verification_lifetime: timedelta | None = None,
        password_reset_lifetime: timedelta | None = None,
    ) -> None:
        self.database_session = database_session

        self.email_verification_lifetime = email_verification_lifetime or timedelta(
            hours=settings.email_verification_expire_hours,
        )

        self.password_reset_lifetime = password_reset_lifetime or timedelta(
            minutes=settings.password_reset_expire_minutes,
        )

        self.email_verification_tokens = EmailVerificationTokenRepository(
            database_session
        )
        self.password_reset_tokens = PasswordResetTokenRepository(database_session)

    async def register(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        display_name: str | None = None,
    ) -> RegistrationResult:
        normalized_email = self._normalize_email(email)
        normalized_first_name = self._normalize_required_name(
            first_name,
            field_name="First name",
        )
        normalized_last_name = self._normalize_required_name(
            last_name,
            field_name="Last name",
        )
        normalized_display_name = self._normalize_optional_name(display_name)

        await self._ensure_email_is_available(normalized_email)

        account_token = generate_account_token(
            lifetime=self.email_verification_lifetime,
        )

        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            display_name=normalized_display_name,
            is_active=True,
            is_verified=False,
        )

        self.database_session.add(user)

        try:
            await self.database_session.flush()

            await self.email_verification_tokens.create(
                user_id=user.id,
                token_digest=account_token.digest,
                expires_at=account_token.expires_at,
            )

            await self.database_session.commit()

        except IntegrityError as exc:
            await self.database_session.rollback()

            raise EmailAlreadyRegisteredError(
                "An account with this email already exists."
            ) from exc

        except Exception:
            await self.database_session.rollback()
            raise

        await self.database_session.refresh(user)

        return RegistrationResult(
            user=user,
            verification_token=account_token.raw_token,
            verification_token_expires_at=account_token.expires_at,
        )

    async def create_email_verification_token(
        self,
        *,
        user: User,
    ) -> AccountToken:
        if not user.is_active:
            raise InactiveAccountError(
                "Email verification is unavailable for this account."
            )

        if user.is_verified:
            raise AccountLifecycleError("This email address is already verified.")

        now = utc_now()

        account_token = generate_account_token(
            lifetime=self.email_verification_lifetime,
        )

        try:
            await self.email_verification_tokens.revoke_active_for_user(
                user_id=user.id,
                revoked_at=now,
            )

            await self.email_verification_tokens.create(
                user_id=user.id,
                token_digest=account_token.digest,
                expires_at=account_token.expires_at,
            )

            await self.database_session.commit()

        except Exception:
            await self.database_session.rollback()
            raise

        return account_token

    async def verify_email(
        self,
        *,
        raw_token: str,
    ) -> EmailVerificationResult:
        try:
            token_digest = digest_account_token(raw_token)
        except ValueError as exc:
            raise InvalidVerificationTokenError(
                "The email-verification token is invalid."
            ) from exc

        try:
            token = await self.email_verification_tokens.get_by_digest_for_update(
                token_digest
            )

            if token is None or not token.is_usable:
                raise InvalidVerificationTokenError(
                    "The email-verification token is invalid or has expired."
                )

            user = token.user

            if not user.is_active:
                raise InactiveAccountError("This account is inactive.")

            now = utc_now()

            if not user.is_verified:
                user.is_verified = True

            await self.email_verification_tokens.consume(
                token,
                consumed_at=now,
            )

            await self.email_verification_tokens.revoke_active_for_user(
                user_id=user.id,
                revoked_at=now,
            )

            await self.database_session.commit()

        except AccountLifecycleError:
            await self.database_session.rollback()
            raise

        except Exception:
            await self.database_session.rollback()
            raise

        await self.database_session.refresh(user)
        await self.database_session.refresh(token)

        return EmailVerificationResult(
            user=user,
            token=token,
        )

    async def request_password_reset(
        self,
        *,
        email: str,
    ) -> PasswordResetRequestResult | None:
        normalized_email = self._normalize_email(email)
        user = await self.get_user_by_email(normalized_email)

        if (
            user is None
            or not user.is_active
            or not user.is_verified
            or user.deleted_at is not None
        ):
            return None

        now = utc_now()
        account_token = generate_account_token(
            lifetime=self.password_reset_lifetime,
        )

        try:
            await self.password_reset_tokens.revoke_active_for_user(
                user_id=user.id,
                revoked_at=now,
            )

            await self.password_reset_tokens.create(
                user_id=user.id,
                token_digest=account_token.digest,
                expires_at=account_token.expires_at,
            )

            await self.database_session.commit()

        except Exception:
            await self.database_session.rollback()
            raise

        return PasswordResetRequestResult(
            reset_token=account_token.raw_token,
            reset_token_expires_at=account_token.expires_at,
        )

    async def reset_password(
        self,
        *,
        raw_token: str,
        new_password: str,
    ) -> PasswordResetResult:
        try:
            token_digest = digest_account_token(raw_token)
        except ValueError as exc:
            raise InvalidPasswordResetTokenError(
                "The password-reset token is invalid."
            ) from exc

        try:
            token = await self.password_reset_tokens.get_by_digest_for_update(
                token_digest
            )

            if token is None or not token.is_usable:
                raise InvalidPasswordResetTokenError(
                    "The password-reset token is invalid or has expired."
                )

            user_statement = (
                select(User)
                .where(
                    User.id == token.user_id,
                    User.deleted_at.is_(None),
                )
                .with_for_update(
                    of=User,
                )
            )

            user_result = await self.database_session.execute(user_statement)
            user = user_result.scalar_one_or_none()

            if user is None or not user.is_active:
                raise InactiveAccountError("This account is inactive.")

            now = utc_now()

            user.password_hash = hash_password(new_password)
            user.password_changed_at = now
            user.failed_login_attempts = 0
            user.locked_until = None

            await self.password_reset_tokens.consume(
                token,
                consumed_at=now,
            )

            await self.password_reset_tokens.revoke_active_for_user(
                user_id=user.id,
                revoked_at=now,
            )

            await refresh_token_repository.revoke_all_for_user(
                self.database_session,
                user.id,
                revoked_at=now,
            )

            await session_repository.revoke_all_for_user(
                self.database_session,
                user.id,
                reason="password_reset",
                revoked_at=now,
            )

            await self.database_session.commit()

        except AccountLifecycleError:
            await self.database_session.rollback()
            raise

        except Exception:
            await self.database_session.rollback()
            raise

        await self.database_session.refresh(user)
        await self.database_session.refresh(token)

        return PasswordResetResult(
            user=user,
            token=token,
        )

    async def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        normalized_email = self._normalize_email(email)

        statement = select(User).where(
            User.email == normalized_email,
            User.deleted_at.is_(None),
        )

        result = await self.database_session.execute(statement)

        return result.scalar_one_or_none()

    async def _ensure_email_is_available(
        self,
        email: str,
    ) -> None:
        existing_user = await self.get_user_by_email(email)

        if existing_user is not None:
            raise EmailAlreadyRegisteredError(
                "An account with this email already exists."
            )

    @staticmethod
    def _normalize_email(email: str) -> str:
        normalized_email = email.strip().lower()

        if not normalized_email:
            raise ValueError("Email address cannot be empty.")

        return normalized_email

    @staticmethod
    def _normalize_required_name(
        value: str,
        *,
        field_name: str,
    ) -> str:
        normalized_value = " ".join(value.split())

        if not normalized_value:
            raise ValueError(f"{field_name} cannot be empty.")

        return normalized_value

    @staticmethod
    def _normalize_optional_name(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = " ".join(value.split())

        return normalized_value or None
