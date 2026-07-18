from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.session import Session
from app.models.user import User
from app.repositories.login_attempt_repository import (
    login_attempt_repository,
)
from app.repositories.refresh_token_repository import (
    refresh_token_repository,
)
from app.repositories.session_repository import (
    session_repository,
)
from app.repositories.user_repository import (
    user_repository,
)
from app.schemas.auth import TokenPair
from app.security.passwords import (
    verify_and_update_password,
)
from app.security.tokens import (
    create_access_token,
    digest_refresh_token,
    generate_refresh_token,
)


class AuthenticationError(Exception):
    status_code: int = 401
    error_code: str = "authentication_failed"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidCredentialsError(AuthenticationError):
    error_code = "invalid_credentials"


class AccountDisabledError(AuthenticationError):
    status_code = 403
    error_code = "account_disabled"


class AccountLockedError(AuthenticationError):
    status_code = 423
    error_code = "account_locked"


class InvalidRefreshTokenError(AuthenticationError):
    error_code = "invalid_refresh_token"


class RefreshTokenReuseError(AuthenticationError):
    error_code = "refresh_token_reuse"


class InvalidSessionError(AuthenticationError):
    error_code = "invalid_session"


@dataclass(frozen=True, slots=True)
class LoginResult:
    user: User
    tokens: TokenPair


@dataclass(frozen=True, slots=True)
class RefreshResult:
    user: User
    tokens: TokenPair


class AuthenticationService:
    async def login(
        self,
        database_session: AsyncSession,
        *,
        email: str,
        password: str,
        ip_address: str | None,
        user_agent: str | None,
        device_name: str | None,
    ) -> LoginResult:
        normalized_email = email.strip().lower()
        now = datetime.now(UTC)

        user = await user_repository.get_by_email(
            database_session,
            normalized_email,
        )

        if user is None:
            await login_attempt_repository.record(
                database_session,
                email=normalized_email,
                user_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                was_successful=False,
                failure_reason="unknown_user",
            )

            await database_session.commit()

            raise InvalidCredentialsError("The email address or password is incorrect.")

        if not user.is_active or user.deleted_at is not None:
            await login_attempt_repository.record(
                database_session,
                email=normalized_email,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                was_successful=False,
                failure_reason="account_disabled",
            )

            await database_session.commit()

            raise AccountDisabledError("This account is disabled.")

        if user.locked_until is not None and user.locked_until > now:
            await login_attempt_repository.record(
                database_session,
                email=normalized_email,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                was_successful=False,
                failure_reason="account_locked",
            )

            await database_session.commit()

            raise AccountLockedError("This account is temporarily locked.")

        password_result = verify_and_update_password(
            password,
            user.password_hash,
        )

        if not password_result.is_valid:
            user.failed_login_attempts += 1

            failure_reason = "invalid_password"

            if user.failed_login_attempts >= settings.maximum_failed_login_attempts:
                user.locked_until = now + timedelta(
                    minutes=settings.account_lockout_minutes,
                )
                failure_reason = "account_locked"

            await login_attempt_repository.record(
                database_session,
                email=normalized_email,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                was_successful=False,
                failure_reason=failure_reason,
            )

            await database_session.commit()

            if failure_reason == "account_locked":
                raise AccountLockedError("This account is temporarily locked.")

            raise InvalidCredentialsError("The email address or password is incorrect.")

        if password_result.updated_hash is not None:
            user.password_hash = password_result.updated_hash
            user.password_changed_at = now

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now

        refresh_token_value = generate_refresh_token(
            now=now,
        )

        authentication_session = Session(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
            last_seen_at=now,
            expires_at=refresh_token_value.expires_at,
            is_active=True,
        )

        database_session.add(authentication_session)
        await database_session.flush()

        token_family_id = uuid4()

        refresh_token_record = RefreshToken(
            user_id=user.id,
            session_id=authentication_session.id,
            token_digest=refresh_token_value.digest,
            family_id=token_family_id,
            expires_at=refresh_token_value.expires_at,
        )

        database_session.add(refresh_token_record)

        await login_attempt_repository.record(
            database_session,
            email=normalized_email,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            was_successful=True,
        )

        access_token = create_access_token(
            user_id=user.id,
            session_id=authentication_session.id,
            now=now,
        )

        await database_session.commit()

        # SQL expressions such as updated_at=func.now() can leave
        # generated attributes expired after a flush or commit.
        # Refresh the user explicitly before Pydantic reads it.
        await database_session.refresh(user)

        return LoginResult(
            user=user,
            tokens=TokenPair(
                access_token=access_token.value,
                refresh_token=refresh_token_value.value,
                access_token_expires_at=access_token.expires_at,
                refresh_token_expires_at=(refresh_token_value.expires_at),
            ),
        )

    async def refresh(
        self,
        database_session: AsyncSession,
        *,
        raw_refresh_token: str,
    ) -> RefreshResult:
        now = datetime.now(UTC)
        token_digest = digest_refresh_token(
            raw_refresh_token,
        )

        stored_token = await refresh_token_repository.get_by_digest(
            database_session,
            token_digest,
        )

        if stored_token is None:
            raise InvalidRefreshTokenError("The refresh token is invalid.")

        if stored_token.used_at is not None or stored_token.revoked_at is not None:
            await refresh_token_repository.revoke_family(
                database_session,
                stored_token.family_id,
                revoked_at=now,
            )

            reused_token_session = stored_token.session

            if reused_token_session is not None:
                await session_repository.revoke(
                    database_session,
                    reused_token_session,
                    reason="refresh_token_reuse",
                    revoked_at=now,
                )

            await database_session.commit()

            raise RefreshTokenReuseError("Refresh-token reuse was detected.")

        if stored_token.expires_at <= now:
            stored_token.revoked_at = now
            await database_session.commit()

            raise InvalidRefreshTokenError("The refresh token has expired.")

        active_session = await session_repository.get_active_by_id(
            database_session,
            stored_token.session_id,
        )

        if active_session is None:
            stored_token.revoked_at = now
            await database_session.commit()

            raise InvalidSessionError("The authentication session is invalid.")

        user = stored_token.user

        if not user.is_active or user.deleted_at is not None:
            await session_repository.revoke(
                database_session,
                active_session,
                reason="account_disabled",
                revoked_at=now,
            )

            await refresh_token_repository.revoke_family(
                database_session,
                stored_token.family_id,
                revoked_at=now,
            )

            await database_session.commit()

            raise AccountDisabledError("This account is disabled.")

        replacement_value = generate_refresh_token(
            now=now,
        )

        replacement_record = RefreshToken(
            user_id=stored_token.user_id,
            session_id=stored_token.session_id,
            token_digest=replacement_value.digest,
            family_id=stored_token.family_id,
            expires_at=replacement_value.expires_at,
        )

        database_session.add(replacement_record)
        await database_session.flush()

        stored_token.used_at = now
        stored_token.replaced_by_token_id = replacement_record.id

        active_session.last_seen_at = now
        active_session.expires_at = replacement_value.expires_at

        access_token = create_access_token(
            user_id=user.id,
            session_id=active_session.id,
            now=now,
        )

        await database_session.commit()

        # Prevent MissingGreenlet when the response schema accesses
        # database-generated attributes such as updated_at.
        await database_session.refresh(user)

        return RefreshResult(
            user=user,
            tokens=TokenPair(
                access_token=access_token.value,
                refresh_token=replacement_value.value,
                access_token_expires_at=access_token.expires_at,
                refresh_token_expires_at=(replacement_value.expires_at),
            ),
        )

    async def logout(
        self,
        database_session: AsyncSession,
        *,
        raw_refresh_token: str,
    ) -> None:
        token_digest = digest_refresh_token(
            raw_refresh_token,
        )

        stored_token = await refresh_token_repository.get_by_digest(
            database_session,
            token_digest,
        )

        if stored_token is None:
            return

        now = datetime.now(UTC)

        await refresh_token_repository.revoke_for_session(
            database_session,
            stored_token.session_id,
            revoked_at=now,
        )

        stored_session = stored_token.session

        if stored_session is not None:
            await session_repository.revoke(
                database_session,
                stored_session,
                reason="user_logout",
                revoked_at=now,
            )

        await database_session.commit()

    async def logout_all(
        self,
        database_session: AsyncSession,
        *,
        user_id: UUID,
    ) -> None:
        now = datetime.now(UTC)

        await refresh_token_repository.revoke_all_for_user(
            database_session,
            user_id,
            revoked_at=now,
        )

        await session_repository.revoke_all_for_user(
            database_session,
            user_id,
            reason="user_logout_all",
            revoked_at=now,
        )

        await database_session.commit()


authentication_service = AuthenticationService()
