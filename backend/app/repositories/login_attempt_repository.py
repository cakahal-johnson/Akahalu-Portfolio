from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_attempt import LoginAttempt
from app.repositories.base import BaseRepository


class LoginAttemptRepository(
    BaseRepository[LoginAttempt],
):
    def __init__(self) -> None:
        super().__init__(LoginAttempt)

    async def record(
        self,
        session: AsyncSession,
        *,
        email: str,
        user_id: UUID | None,
        ip_address: str | None,
        user_agent: str | None,
        was_successful: bool,
        failure_reason: str | None = None,
    ) -> LoginAttempt:
        attempt = LoginAttempt(
            email=email.lower(),
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            was_successful=was_successful,
            failure_reason=failure_reason,
        )

        session.add(attempt)
        await session.flush()

        return attempt


login_attempt_repository = LoginAttemptRepository()
