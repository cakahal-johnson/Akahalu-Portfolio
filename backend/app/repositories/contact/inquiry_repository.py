from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.roles import ExpressionElementRole

from app.models.contact_inquiry import ContactInquiry
from app.repositories.base import BaseRepository


class ContactInquiryRepository(
    BaseRepository[ContactInquiry],
):
    def __init__(self) -> None:
        super().__init__(
            ContactInquiry,
        )

    async def get_by_id(
        self,
        session: AsyncSession,
        inquiry_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ContactInquiry | None:
        statement = select(
            ContactInquiry,
        ).where(
            ContactInquiry.id == inquiry_id,
        )

        if not include_deleted:
            statement = statement.where(
                ContactInquiry.deleted_at.is_(None),
            )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

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
        filters = self._build_admin_filters(
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
        )

        statement = select(
            ContactInquiry,
        ).where(
            *filters,
        )

        count_statement = select(
            func.count(
                ContactInquiry.id,
            )
        ).where(
            *filters,
        )

        statement = self._apply_admin_sorting(
            statement,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

        statement = statement.offset(
            offset,
        ).limit(
            limit,
        )

        result = await session.execute(
            statement,
        )

        count_result = await session.execute(
            count_statement,
        )

        return (
            result.scalars().unique().all(),
            count_result.scalar_one(),
        )

    async def find_recent_duplicate(
        self,
        session: AsyncSession,
        *,
        submission_fingerprint: str,
        created_after: datetime,
    ) -> ContactInquiry | None:
        statement = (
            select(
                ContactInquiry,
            )
            .where(
                ContactInquiry.submission_fingerprint == submission_fingerprint,
                ContactInquiry.created_at >= created_after,
                ContactInquiry.deleted_at.is_(None),
            )
            .order_by(
                ContactInquiry.created_at.desc(),
            )
            .limit(1)
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def count_by_status(
        self,
        session: AsyncSession,
        *,
        inquiry_status: str,
        include_deleted: bool = False,
    ) -> int:
        statement = select(
            func.count(
                ContactInquiry.id,
            )
        ).where(
            ContactInquiry.status == inquiry_status,
        )

        if not include_deleted:
            statement = statement.where(
                ContactInquiry.deleted_at.is_(None),
            )

        result = await session.execute(
            statement,
        )

        return result.scalar_one()

    async def count_unread(
        self,
        session: AsyncSession,
    ) -> int:
        statement = select(
            func.count(
                ContactInquiry.id,
            )
        ).where(
            ContactInquiry.is_read.is_(False),
            ContactInquiry.deleted_at.is_(None),
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one()

    async def count_requires_attention(
        self,
        session: AsyncSession,
    ) -> int:
        statement = select(
            func.count(
                ContactInquiry.id,
            )
        ).where(
            ContactInquiry.status.in_(
                (
                    "new",
                    "in_progress",
                )
            ),
            ContactInquiry.priority.in_(
                (
                    "high",
                    "urgent",
                )
            ),
            ContactInquiry.deleted_at.is_(None),
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one()

    @staticmethod
    def _build_admin_filters(
        *,
        search: str | None,
        inquiry_type: str | None,
        inquiry_status: str | None,
        priority: str | None,
        is_read: bool | None,
        assigned_to_id: UUID | None,
        project_id: UUID | None,
        include_unassigned: bool,
        include_deleted: bool,
        created_from: datetime | None,
        created_to: datetime | None,
    ) -> list[ExpressionElementRole[bool]]:
        filters: list[ExpressionElementRole[bool]] = []

        if not include_deleted:
            filters.append(
                ContactInquiry.deleted_at.is_(None),
            )

        if search:
            normalized_search = search.strip()

            if normalized_search:
                search_pattern = f"%{normalized_search}%"

                filters.append(
                    or_(
                        ContactInquiry.name.ilike(
                            search_pattern,
                        ),
                        ContactInquiry.email.ilike(
                            search_pattern,
                        ),
                        ContactInquiry.phone.ilike(
                            search_pattern,
                        ),
                        ContactInquiry.company.ilike(
                            search_pattern,
                        ),
                        ContactInquiry.subject.ilike(
                            search_pattern,
                        ),
                        ContactInquiry.message.ilike(
                            search_pattern,
                        ),
                        ContactInquiry.internal_notes.ilike(
                            search_pattern,
                        ),
                    )
                )

        if inquiry_type is not None:
            filters.append(
                ContactInquiry.inquiry_type == inquiry_type,
            )

        if inquiry_status is not None:
            filters.append(
                ContactInquiry.status == inquiry_status,
            )

        if priority is not None:
            filters.append(
                ContactInquiry.priority == priority,
            )

        if is_read is not None:
            filters.append(
                ContactInquiry.is_read.is_(
                    is_read,
                )
            )

        if assigned_to_id is not None:
            if include_unassigned:
                filters.append(
                    or_(
                        ContactInquiry.assigned_to_id == assigned_to_id,
                        ContactInquiry.assigned_to_id.is_(None),
                    )
                )
            else:
                filters.append(
                    ContactInquiry.assigned_to_id == assigned_to_id,
                )
        elif include_unassigned:
            filters.append(
                ContactInquiry.assigned_to_id.is_(None),
            )

        if project_id is not None:
            filters.append(
                ContactInquiry.project_id == project_id,
            )

        if created_from is not None:
            filters.append(
                ContactInquiry.created_at >= created_from,
            )

        if created_to is not None:
            filters.append(
                ContactInquiry.created_at <= created_to,
            )

        return filters

    @staticmethod
    def _apply_admin_sorting(
        statement: Select[tuple[ContactInquiry]],
        *,
        sort_by: str,
        sort_direction: str,
    ) -> Select[tuple[ContactInquiry]]:
        sortable_columns = {
            "name": ContactInquiry.name,
            "email": ContactInquiry.email,
            "subject": ContactInquiry.subject,
            "inquiry_type": ContactInquiry.inquiry_type,
            "status": ContactInquiry.status,
            "priority": ContactInquiry.priority,
            "is_read": ContactInquiry.is_read,
            "created_at": ContactInquiry.created_at,
            "updated_at": ContactInquiry.updated_at,
        }

        sort_column = sortable_columns.get(
            sort_by,
            ContactInquiry.created_at,
        )

        if sort_direction == "asc":
            order_expression = sort_column.asc()
        else:
            order_expression = sort_column.desc()

        return statement.order_by(
            order_expression,
            ContactInquiry.created_at.desc(),
            ContactInquiry.id.asc(),
        )


contact_inquiry_repository = ContactInquiryRepository()
