from __future__ import annotations

import hashlib
import hmac
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import raiseload

from app.core.config import settings
from app.models.contact_inquiry import ContactInquiry
from app.models.project import Project
from app.models.user import User
from app.repositories.contact import contact_inquiry_repository
from app.schemas.contact import (
    ContactInquiryPublicCreate,
    ContactInquiryReadUpdate,
    ContactInquiryRestoreRequest,
    ContactInquiryStatus,
    ContactInquiryStatusUpdate,
    ContactInquiryUpdate,
)


class ContactInquiryError(Exception):
    status_code: int = 400
    error_code: str = "contact_inquiry_operation_failed"

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(message)

        self.message = message


class ContactInquiryNotFoundError(ContactInquiryError):
    status_code = 404
    error_code = "contact_inquiry_not_found"


class ContactInquiryConflictError(ContactInquiryError):
    status_code = 409
    error_code = "contact_inquiry_conflict"


class ContactInquiryDuplicateError(ContactInquiryConflictError):
    error_code = "contact_inquiry_duplicate"


class ContactInquiryHoneypotError(ContactInquiryError):
    status_code = 422
    error_code = "contact_inquiry_invalid_submission"


class ContactInquiryInvalidTransitionError(ContactInquiryError):
    status_code = 409
    error_code = "contact_inquiry_invalid_status_transition"


class ContactInquiryProjectNotFoundError(ContactInquiryError):
    status_code = 404
    error_code = "contact_inquiry_project_not_found"


class ContactInquiryAssigneeNotFoundError(ContactInquiryError):
    status_code = 404
    error_code = "contact_inquiry_assignee_not_found"


class ContactInquiryAssigneeInactiveError(ContactInquiryError):
    status_code = 409
    error_code = "contact_inquiry_assignee_inactive"


class ContactInquiryService:
    duplicate_window = timedelta(
        minutes=settings.contact_duplicate_window_minutes,
    )

    allowed_status_transitions: dict[
        str,
        set[str],
    ] = {
        ContactInquiryStatus.NEW.value: {
            ContactInquiryStatus.IN_PROGRESS.value,
            ContactInquiryStatus.RESPONDED.value,
            ContactInquiryStatus.CLOSED.value,
            ContactInquiryStatus.SPAM.value,
        },
        ContactInquiryStatus.IN_PROGRESS.value: {
            ContactInquiryStatus.NEW.value,
            ContactInquiryStatus.RESPONDED.value,
            ContactInquiryStatus.CLOSED.value,
            ContactInquiryStatus.SPAM.value,
        },
        ContactInquiryStatus.RESPONDED.value: {
            ContactInquiryStatus.IN_PROGRESS.value,
            ContactInquiryStatus.CLOSED.value,
            ContactInquiryStatus.SPAM.value,
        },
        ContactInquiryStatus.CLOSED.value: {
            ContactInquiryStatus.IN_PROGRESS.value,
            ContactInquiryStatus.SPAM.value,
        },
        ContactInquiryStatus.SPAM.value: {
            ContactInquiryStatus.NEW.value,
            ContactInquiryStatus.IN_PROGRESS.value,
        },
    }

    async def get_by_id(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ContactInquiry:
        inquiry = await contact_inquiry_repository.get_by_id(
            session,
            inquiry_id,
            include_deleted=include_deleted,
        )

        if inquiry is None:
            raise ContactInquiryNotFoundError(
                "The requested contact inquiry was not found.",
            )

        return inquiry

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        inquiry_type: str | None = None,
        inquiry_status: str | None = None,
        priority: str | None = None,
        is_read: bool | None = None,
        assigned_to_id: UUID | None = None,
        project_id: UUID | None = None,
        include_unassigned: bool = False,
        include_deleted: bool = False,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[
        Sequence[ContactInquiry],
        int,
    ]:
        if created_from is not None and created_to is not None:
            if created_from > created_to:
                raise ContactInquiryConflictError(
                    "The created-from date cannot be later than the created-to date.",
                )

        return await contact_inquiry_repository.list_for_admin(
            session,
            offset=offset,
            limit=limit,
            search=search,
            inquiry_type=inquiry_type,
            inquiry_status=inquiry_status,
            priority=priority,
            is_read=is_read,
            assigned_to_id=assigned_to_id,
            project_id=project_id,
            include_unassigned=include_unassigned,
            include_deleted=include_deleted,
            created_from=created_from,
            created_to=created_to,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def list_assignee_options(
        self,
        session: AsyncSession,
    ) -> Sequence[User]:
        statement = (
            select(
                User,
            )
            .options(
                raiseload("*"),
            )
            .where(
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            )
            .order_by(
                User.first_name.asc(),
                User.last_name.asc(),
                User.email.asc(),
                User.id.asc(),
            )
        )

        result = await session.execute(
            statement,
        )

        return result.scalars().all()

    async def list_project_options(
        self,
        session: AsyncSession,
    ) -> Sequence[Project]:
        statement = (
            select(
                Project,
            )
            .options(
                raiseload("*"),
            )
            .where(
                Project.deleted_at.is_(None),
            )
            .order_by(
                Project.title.asc(),
                Project.id.asc(),
            )
        )

        result = await session.execute(
            statement,
        )

        return result.scalars().all()

    async def create_public(
        self,
        session: AsyncSession,
        payload: ContactInquiryPublicCreate,
        *,
        client_ip: str | None = None,
        user_agent: str | None = None,
        hash_secret: str,
    ) -> ContactInquiry:
        self._validate_honeypot(
            payload.website,
        )

        if payload.project_id is not None:
            await self._validate_public_project(
                session,
                payload.project_id,
            )

        ip_address_hash = self.hash_sensitive_value(
            client_ip,
            secret=hash_secret,
        )

        submission_fingerprint = self.build_submission_fingerprint(
            email=str(payload.email),
            subject=payload.subject,
            message=payload.message,
            client_ip=client_ip,
            secret=hash_secret,
        )

        duplicate = await contact_inquiry_repository.find_recent_duplicate(
            session,
            submission_fingerprint=submission_fingerprint,
            created_after=datetime.now(UTC) - self.duplicate_window,
        )

        if duplicate is not None:
            raise ContactInquiryDuplicateError(
                "An identical contact inquiry was submitted recently.",
            )

        inquiry = ContactInquiry(
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            company=payload.company,
            subject=payload.subject,
            message=payload.message,
            inquiry_type=payload.inquiry_type.value,
            status=ContactInquiryStatus.NEW.value,
            priority="normal",
            project_id=payload.project_id,
            consent_given=payload.consent_given,
            source_page=payload.source_page,
            user_agent=self._normalize_user_agent(
                user_agent,
            ),
            ip_address_hash=ip_address_hash,
            submission_fingerprint=submission_fingerprint,
        )

        return await contact_inquiry_repository.add(
            session,
            inquiry,
        )

    async def update(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
        payload: ContactInquiryUpdate,
    ) -> ContactInquiry:
        inquiry = await self.get_by_id(
            session,
            inquiry_id,
        )

        changes = payload.model_dump(
            exclude_unset=True,
        )

        if "assigned_to_id" in changes:
            assigned_to_id = changes["assigned_to_id"]

            if assigned_to_id is not None:
                await self._validate_assignee(
                    session,
                    assigned_to_id,
                )

        for field_name, value in changes.items():
            if hasattr(value, "value"):
                value = value.value

            setattr(
                inquiry,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(
            inquiry,
        )

        return inquiry

    async def set_read_state(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
        payload: ContactInquiryReadUpdate,
    ) -> ContactInquiry:
        inquiry = await self.get_by_id(
            session,
            inquiry_id,
        )

        if inquiry.is_read == payload.is_read:
            return inquiry

        inquiry.is_read = payload.is_read
        inquiry.read_at = datetime.now(UTC) if payload.is_read else None

        await session.flush()
        await session.refresh(
            inquiry,
        )

        return inquiry

    async def update_status(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
        payload: ContactInquiryStatusUpdate,
    ) -> ContactInquiry:
        inquiry = await self.get_by_id(
            session,
            inquiry_id,
        )

        requested_status = payload.status.value

        if inquiry.status == requested_status:
            return inquiry

        self._validate_status_transition(
            current_status=inquiry.status,
            requested_status=requested_status,
        )

        now = datetime.now(UTC)

        inquiry.status = requested_status

        if requested_status == ContactInquiryStatus.RESPONDED.value:
            inquiry.responded_at = now
            inquiry.closed_at = None
            inquiry.is_read = True
            inquiry.read_at = inquiry.read_at or now

        elif requested_status == ContactInquiryStatus.CLOSED.value:
            inquiry.closed_at = now
            inquiry.is_read = True
            inquiry.read_at = inquiry.read_at or now

        elif requested_status == ContactInquiryStatus.SPAM.value:
            inquiry.closed_at = None
            inquiry.is_read = True
            inquiry.read_at = inquiry.read_at or now

        elif requested_status == ContactInquiryStatus.NEW.value:
            inquiry.responded_at = None
            inquiry.closed_at = None

        elif requested_status == ContactInquiryStatus.IN_PROGRESS.value:
            inquiry.closed_at = None

        await session.flush()
        await session.refresh(
            inquiry,
        )

        return inquiry

    async def soft_delete(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
    ) -> ContactInquiry:
        inquiry = await self.get_by_id(
            session,
            inquiry_id,
        )

        inquiry.soft_delete()

        await session.flush()
        await session.refresh(
            inquiry,
        )

        return inquiry

    async def restore(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
        payload: ContactInquiryRestoreRequest,
    ) -> ContactInquiry:
        inquiry = await self.get_by_id(
            session,
            inquiry_id,
            include_deleted=True,
        )

        if inquiry.deleted_at is None:
            raise ContactInquiryConflictError(
                "The contact inquiry is not deleted.",
            )

        restored_status = payload.status.value
        now = datetime.now(UTC)

        inquiry.restore()
        inquiry.status = restored_status
        inquiry.priority = payload.priority.value

        inquiry.responded_at = None
        inquiry.closed_at = None

        if restored_status == ContactInquiryStatus.SPAM.value:
            inquiry.is_read = True
            inquiry.read_at = inquiry.read_at or now

        await session.flush()
        await session.refresh(
            inquiry,
        )

        return inquiry

    async def count_by_status(
        self,
        session: AsyncSession,
        inquiry_status: ContactInquiryStatus,
    ) -> int:
        return await contact_inquiry_repository.count_by_status(
            session,
            inquiry_status=inquiry_status.value,
        )

    async def count_unread(
        self,
        session: AsyncSession,
    ) -> int:
        return await contact_inquiry_repository.count_unread(
            session,
        )

    async def count_requires_attention(
        self,
        session: AsyncSession,
    ) -> int:
        return await contact_inquiry_repository.count_requires_attention(
            session,
        )

    @staticmethod
    def hash_sensitive_value(
        value: str | None,
        *,
        secret: str,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip().lower()

        if not normalized_value:
            return None

        return hmac.new(
            secret.encode("utf-8"),
            normalized_value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    def build_submission_fingerprint(
        cls,
        *,
        email: str,
        subject: str,
        message: str,
        client_ip: str | None,
        secret: str,
    ) -> str:
        fingerprint_parts = (
            email.strip().lower(),
            " ".join(subject.lower().split()),
            " ".join(message.lower().split()),
            (client_ip or "").strip().lower(),
        )

        fingerprint_value = "\x1f".join(
            fingerprint_parts,
        )

        fingerprint = cls.hash_sensitive_value(
            fingerprint_value,
            secret=secret,
        )

        if fingerprint is None:
            raise ContactInquiryConflictError(
                "The contact inquiry fingerprint could not be generated.",
            )

        return fingerprint

    @staticmethod
    def _validate_honeypot(
        honeypot_value: str | None,
    ) -> None:
        if honeypot_value:
            raise ContactInquiryHoneypotError(
                "The contact inquiry submission was invalid.",
            )

    @staticmethod
    def _validate_status_transition(
        *,
        current_status: str,
        requested_status: str,
    ) -> None:
        allowed_statuses = ContactInquiryService.allowed_status_transitions.get(
            current_status,
            set(),
        )

        if requested_status not in allowed_statuses:
            raise ContactInquiryInvalidTransitionError(
                "The contact inquiry cannot transition from "
                f"{current_status!r} to {requested_status!r}.",
            )

    @staticmethod
    async def _validate_public_project(
        session: AsyncSession,
        project_id: UUID,
    ) -> Project:
        """
        Return an available public portfolio project.

        Public contact submissions may reference only projects that are
        published, publicly visible, not soft-deleted, and have a
        publication timestamp.

        Relationship loading is blocked because this validation needs
        Project column values only.
        """

        statement = (
            select(
                Project,
            )
            .options(
                raiseload("*"),
            )
            .where(
                Project.id == project_id,
                Project.deleted_at.is_(None),
                Project.status == "published",
                Project.visibility == "public",
                Project.published_at.is_not(None),
            )
        )

        result = await session.execute(
            statement,
        )

        project = result.scalar_one_or_none()

        if project is None:
            raise ContactInquiryProjectNotFoundError(
                "The selected portfolio project was not found.",
            )

        return project

    @staticmethod
    async def _validate_assignee(
        session: AsyncSession,
        user_id: UUID,
    ) -> User:
        """
        Return an active, non-deleted inquiry assignee.

        Relationship loading is blocked because assignment validation
        requires User column values only.
        """

        statement = (
            select(
                User,
            )
            .options(
                raiseload("*"),
            )
            .where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )

        result = await session.execute(
            statement,
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise ContactInquiryAssigneeNotFoundError(
                "The selected inquiry assignee was not found.",
            )

        if not user.is_active:
            raise ContactInquiryAssigneeInactiveError(
                "The selected inquiry assignee is inactive.",
            )

        return user

    @staticmethod
    def _normalize_user_agent(
        user_agent: str | None,
    ) -> str | None:
        if user_agent is None:
            return None

        normalized_user_agent = " ".join(
            user_agent.split(),
        )

        if not normalized_user_agent:
            return None

        return normalized_user_agent[: settings.contact_user_agent_max_length]


contact_inquiry_service = ContactInquiryService()
