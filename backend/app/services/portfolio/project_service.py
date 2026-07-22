from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypedDict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_associations import (
    ProjectTechnologyAssociation,
)
from app.models.project_category import ProjectCategory
from app.models.project_technology import ProjectTechnology
from app.repositories.portfolio.project_category_repository import (
    ProjectCategoryRepository,
    project_category_repository,
)
from app.repositories.portfolio.project_repository import (
    ProjectRepository,
    project_repository,
)
from app.repositories.portfolio.project_technology_repository import (
    ProjectTechnologyRepository,
    project_technology_repository,
)
from app.schemas.portfolio.project import (
    ProjectCreate,
    ProjectUpdate,
)


class TechnologyAssignmentData(TypedDict):
    """Normalized project-technology assignment data."""

    technology_id: UUID
    is_featured: bool
    sort_order: int


class ProjectNotFoundError(Exception):
    """Raised when a requested portfolio project does not exist."""


class ProjectConflictError(Exception):
    """Raised when project data violates a uniqueness rule."""


class ProjectCategoryNotFoundError(Exception):
    """Raised when a selected project category does not exist."""


class ProjectCategoryUnavailableError(Exception):
    """Raised when a selected project category is inactive."""


class ProjectTechnologyNotFoundError(Exception):
    """Raised when a selected project technology does not exist."""


class ProjectTechnologyUnavailableError(Exception):
    """Raised when a selected project technology is inactive."""


class ProjectPublicationError(Exception):
    """Raised when a project cannot enter a publication state."""


class ProjectService:
    """Coordinate the complete portfolio-project lifecycle."""

    def __init__(
        self,
        repository: ProjectRepository,
        categories: ProjectCategoryRepository,
        technologies: ProjectTechnologyRepository,
    ) -> None:
        self.repository = repository
        self.categories = categories
        self.technologies = technologies

    async def get_by_id(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_deleted: bool = False,
        include_related: bool = True,
    ) -> Project:
        """Return a project by ID or raise a not-found error."""

        project = await self.repository.get_by_id(
            session,
            project_id,
            include_deleted=include_deleted,
            include_related=include_related,
        )

        if project is None:
            raise ProjectNotFoundError(
                "Portfolio project was not found.",
            )

        return project

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
        include_related: bool = True,
    ) -> Project:
        """Return a project by slug or raise a not-found error."""

        normalized_slug = self._normalize_slug(
            slug,
        )

        project = await self.repository.get_by_slug(
            session,
            normalized_slug,
            include_deleted=include_deleted,
            include_related=include_related,
        )

        if project is None:
            raise ProjectNotFoundError(
                "Portfolio project was not found.",
            )

        return project

    async def get_public_by_slug(
        self,
        session: AsyncSession,
        slug: str,
    ) -> Project:
        """Return a publicly accessible project by slug."""

        normalized_slug = self._normalize_slug(
            slug,
        )

        project = await self.repository.get_public_by_slug(
            session,
            normalized_slug,
        )

        if project is None:
            raise ProjectNotFoundError(
                "Published portfolio project was not found.",
            )

        return project

    async def list_public(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        category_id: UUID | None = None,
        category_slug: str | None = None,
        technology_id: UUID | None = None,
        technology_slug: str | None = None,
        is_featured: bool | None = None,
    ) -> tuple[Sequence[Project], int]:
        """Return paginated publicly accessible projects."""

        return await self.repository.list_public(
            session,
            offset=offset,
            limit=limit,
            search=search,
            category_id=category_id,
            category_slug=self._normalize_optional_slug(
                category_slug,
            ),
            technology_id=technology_id,
            technology_slug=self._normalize_optional_slug(
                technology_slug,
            ),
            is_featured=is_featured,
        )

    async def list_featured(
        self,
        session: AsyncSession,
        *,
        limit: int,
    ) -> Sequence[Project]:
        """Return featured public projects."""

        return await self.repository.list_featured(
            session,
            limit=limit,
        )

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        category_id: UUID | None = None,
        status: str | None = None,
        visibility: str | None = None,
        is_featured: bool | None = None,
        technology_id: UUID | None = None,
        include_deleted: bool = False,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[Sequence[Project], int]:
        """Return paginated projects for administrative management."""

        return await self.repository.list_for_admin(
            session,
            offset=offset,
            limit=limit,
            search=search,
            category_id=category_id,
            status=self._normalize_optional_value(
                status,
            ),
            visibility=self._normalize_optional_value(
                visibility,
            ),
            is_featured=is_featured,
            technology_id=technology_id,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def create(
        self,
        session: AsyncSession,
        payload: ProjectCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> Project:
        """
        Create and flush a portfolio project.

        Transaction commit remains the responsibility of the API or
        unit-of-work boundary.
        """

        data = payload.model_dump(
            mode="json",
        )

        technology_assignments = self._extract_technology_assignments(
            data,
        )

        title = self._normalize_title(
            str(data["title"]),
        )
        slug = self._normalize_slug(
            str(data["slug"]),
        )

        await self._ensure_slug_available(
            session,
            slug,
        )

        category_id = self._coerce_optional_uuid(
            data.get("category_id"),
        )

        category = await self._get_available_category(
            session,
            category_id,
        )

        technologies = await self._get_available_technologies(
            session,
            [assignment["technology_id"] for assignment in technology_assignments],
        )

        data["title"] = title
        data["slug"] = slug
        data["category_id"] = category.id if category is not None else None

        self._normalize_project_dates(
            data,
        )

        self._apply_publication_state(
            data,
        )

        if actor_user_id is not None:
            data["created_by_id"] = actor_user_id
            data["updated_by_id"] = actor_user_id

        if self._is_published_data(data):
            self._validate_publication_data(
                data,
                category,
            )

        project = Project(
            **data,
        )

        session.add(
            project,
        )

        await session.flush()

        self._create_technology_associations(
            project,
            technologies,
            technology_assignments,
        )

        await session.flush()
        await session.refresh(
            project,
        )

        return await self.get_by_id(
            session,
            project.id,
        )

    async def update(
        self,
        session: AsyncSession,
        project_id: UUID,
        payload: ProjectUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> Project:
        """Update and flush an existing portfolio project."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        data = payload.model_dump(
            mode="json",
            exclude_unset=True,
        )

        technology_assignments_present = "technology_assignments" in data

        technology_assignments = self._extract_technology_assignments(
            data,
        )

        if "title" in data:
            data["title"] = self._normalize_title(
                str(data["title"]),
            )

        if "slug" in data:
            normalized_slug = self._normalize_slug(
                str(data["slug"]),
            )

            await self._ensure_slug_available(
                session,
                normalized_slug,
                exclude_project_id=project.id,
            )

            data["slug"] = normalized_slug

        selected_category: ProjectCategory | None = None

        if "category_id" in data:
            category_id = self._coerce_optional_uuid(
                data["category_id"],
            )

            selected_category = await self._get_available_category(
                session,
                category_id,
            )

            data["category_id"] = (
                selected_category.id if selected_category is not None else None
            )
        elif project.category_id is not None:
            selected_category = await self._get_available_category(
                session,
                project.category_id,
            )

        self._normalize_project_dates(
            data,
        )

        if technology_assignments_present:
            technologies = await self._get_available_technologies(
                session,
                [assignment["technology_id"] for assignment in technology_assignments],
            )

            await self._replace_technology_associations(
                session,
                project,
                technologies,
                technology_assignments,
            )

        self._apply_publication_state(
            data,
            current_project=project,
        )

        if actor_user_id is not None:
            data["updated_by_id"] = actor_user_id

        if self._will_be_published(
            project,
            data,
        ):
            self._validate_publication_data(
                data,
                selected_category,
                current_project=project,
            )

        for field_name, value in data.items():
            setattr(
                project,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(
            project,
        )

        return await self.get_by_id(
            session,
            project.id,
        )

    async def replace_technologies(
        self,
        session: AsyncSession,
        project_id: UUID,
        technology_ids: Sequence[UUID],
        *,
        actor_user_id: UUID | None = None,
    ) -> Project:
        """Replace every active technology assignment for a project."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        technologies = await self._get_available_technologies(
            session,
            technology_ids,
        )

        assignments = [
            TechnologyAssignmentData(
                technology_id=technology.id,
                is_featured=False,
                sort_order=sort_order,
            )
            for sort_order, technology in enumerate(
                technologies,
            )
        ]

        await self._replace_technology_associations(
            session,
            project,
            technologies,
            assignments,
        )

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            project,
        )

        return await self.get_by_id(
            session,
            project.id,
        )

    async def publish(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        actor_user_id: UUID | None = None,
        visibility: str = "public",
        published_at: datetime | None = None,
    ) -> Project:
        """Publish a project after validating publication requirements."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        normalized_visibility = self._normalize_value(
            visibility,
        )

        if normalized_visibility not in {
            "public",
            "unlisted",
        }:
            raise ProjectPublicationError(
                "Published projects must be public or unlisted.",
            )

        await self._validate_publication_requirements(
            session,
            project,
        )

        project.status = "published"
        project.visibility = normalized_visibility
        project.published_at = published_at or project.published_at or datetime.now(UTC)

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            project,
        )

        return await self.get_by_id(
            session,
            project.id,
        )

    async def unpublish(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        actor_user_id: UUID | None = None,
        clear_published_at: bool = True,
    ) -> Project:
        """Return a published project to draft status."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        project.status = "draft"
        project.visibility = "private"
        project.is_featured = False

        if clear_published_at:
            project.published_at = None

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            project,
        )

        return project

    async def archive(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> Project:
        """Archive a project and remove it from public visibility."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        project.status = "archived"
        project.visibility = "private"
        project.is_featured = False

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            project,
        )

        return project

    async def set_featured(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        is_featured: bool,
        actor_user_id: UUID | None = None,
    ) -> Project:
        """Set a project's featured state."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        if is_featured and project.status != "published":
            raise ProjectPublicationError(
                "Only published projects can be featured.",
            )

        if is_featured and project.visibility != "public":
            raise ProjectPublicationError(
                "Only public projects can be featured.",
            )

        project.is_featured = is_featured

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            project,
        )

        return project

    async def soft_delete(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> Project:
        """Soft-delete a portfolio project and active associations."""

        project = await self.get_by_id(
            session,
            project_id,
        )

        project.status = "archived"
        project.visibility = "private"
        project.is_featured = False

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        project.soft_delete()

        for association in project.technology_associations:
            if association.deleted_at is None:
                association.soft_delete()

        await session.flush()
        await session.refresh(
            project,
        )

        return project

    async def restore(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        actor_user_id: UUID | None = None,
        restore_as_draft: bool = True,
    ) -> Project:
        """Restore a soft-deleted project after conflict checks."""

        project = await self.get_by_id(
            session,
            project_id,
            include_deleted=True,
        )

        if project.deleted_at is None:
            return project

        await self._ensure_slug_available(
            session,
            project.slug,
            exclude_project_id=project.id,
        )

        if project.category_id is not None:
            await self._get_available_category(
                session,
                project.category_id,
            )

        project.restore()

        if restore_as_draft:
            project.status = "draft"
            project.visibility = "private"
            project.is_featured = False
            project.published_at = None

        if actor_user_id is not None:
            project.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            project,
        )

        return await self.get_by_id(
            session,
            project.id,
        )

    async def count_public(
        self,
        session: AsyncSession,
        *,
        category_id: UUID | None = None,
        is_featured: bool | None = None,
    ) -> int:
        """Count public projects matching the supplied filters."""

        return await self.repository.count_public(
            session,
            category_id=category_id,
            is_featured=is_featured,
        )

    async def _get_available_category(
        self,
        session: AsyncSession,
        category_id: UUID | None,
    ) -> ProjectCategory | None:
        """Return an active category when a category is selected."""

        if category_id is None:
            return None

        category = await self.categories.get_by_id(
            session,
            category_id,
        )

        if category is None:
            raise ProjectCategoryNotFoundError(
                "The selected project category was not found.",
            )

        if not category.is_active:
            raise ProjectCategoryUnavailableError(
                "The selected project category is inactive.",
            )

        return category

    async def _get_available_technologies(
        self,
        session: AsyncSession,
        technology_ids: Sequence[UUID],
    ) -> list[ProjectTechnology]:
        """Resolve unique active technologies while preserving order."""

        technologies: list[ProjectTechnology] = []
        seen_ids: set[UUID] = set()

        for technology_id in technology_ids:
            if technology_id in seen_ids:
                continue

            technology = await self.technologies.get_by_id(
                session,
                technology_id,
            )

            if technology is None:
                raise ProjectTechnologyNotFoundError(
                    f"Project technology {technology_id} was not found.",
                )

            if not technology.is_active:
                raise ProjectTechnologyUnavailableError(
                    f"Project technology {technology.name} is inactive.",
                )

            seen_ids.add(
                technology_id,
            )
            technologies.append(
                technology,
            )

        return technologies

    async def _validate_publication_requirements(
        self,
        session: AsyncSession,
        project: Project,
    ) -> None:
        """Validate requirements for publishing an existing project."""

        if project.category_id is None:
            raise ProjectPublicationError(
                "A project category is required before publication.",
            )

        await self._get_available_category(
            session,
            project.category_id,
        )

        if not project.title.strip():
            raise ProjectPublicationError(
                "A project title is required before publication.",
            )

        if not project.short_description.strip():
            raise ProjectPublicationError(
                "A short description is required before publication.",
            )

        if not project.description.strip():
            raise ProjectPublicationError(
                "A full description is required before publication.",
            )

    async def _ensure_slug_available(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_project_id: UUID | None = None,
    ) -> None:
        """Ensure another non-deleted project does not use the slug."""

        slug_exists = await self.repository.slug_exists(
            session,
            slug,
            exclude_project_id=exclude_project_id,
        )

        if slug_exists:
            raise ProjectConflictError(
                "A portfolio project with this slug already exists.",
            )

    async def _replace_technology_associations(
        self,
        session: AsyncSession,
        project: Project,
        technologies: Sequence[ProjectTechnology],
        assignments: Sequence[TechnologyAssignmentData],
    ) -> None:
        """Replace active assignments while preserving deleted history."""

        assignment_by_id = {
            assignment["technology_id"]: assignment for assignment in assignments
        }

        desired_ids = set(
            assignment_by_id,
        )

        existing_by_technology_id = {
            association.technology_id: association
            for association in project.technology_associations
        }

        for association in project.technology_associations:
            if (
                association.deleted_at is None
                and association.technology_id not in desired_ids
            ):
                association.soft_delete()

        for technology in technologies:
            assignment = assignment_by_id[technology.id]

            existing_association = existing_by_technology_id.get(
                technology.id,
            )

            if existing_association is None:
                project.technology_associations.append(
                    ProjectTechnologyAssociation(
                        project_id=project.id,
                        technology_id=technology.id,
                        sort_order=assignment["sort_order"],
                        is_featured=assignment["is_featured"],
                    )
                )
                continue

            if existing_association.deleted_at is not None:
                existing_association.restore()

            existing_association.sort_order = assignment["sort_order"]
            existing_association.is_featured = assignment["is_featured"]

        await session.flush()

    @staticmethod
    def _create_technology_associations(
        project: Project,
        technologies: Sequence[ProjectTechnology],
        assignments: Sequence[TechnologyAssignmentData],
    ) -> None:
        """Create ordered technology assignments for a new project."""

        assignment_by_id = {
            assignment["technology_id"]: assignment for assignment in assignments
        }

        for technology in technologies:
            assignment = assignment_by_id[technology.id]

            project.technology_associations.append(
                ProjectTechnologyAssociation(
                    technology_id=technology.id,
                    sort_order=assignment["sort_order"],
                    is_featured=assignment["is_featured"],
                )
            )

    @staticmethod
    def _apply_publication_state(
        data: dict[str, object],
        *,
        current_project: Project | None = None,
    ) -> None:
        """Synchronize status, visibility, featured state and timestamp."""

        current_status = (
            current_project.status if current_project is not None else "draft"
        )

        current_visibility = (
            current_project.visibility if current_project is not None else "private"
        )

        status = (
            str(
                data.get(
                    "status",
                    current_status,
                )
            )
            .strip()
            .lower()
        )

        visibility = (
            str(
                data.get(
                    "visibility",
                    current_visibility,
                )
            )
            .strip()
            .lower()
        )

        data["status"] = status
        data["visibility"] = visibility

        if status == "published":
            if visibility == "private":
                raise ProjectPublicationError(
                    "A published project cannot have private visibility.",
                )

            existing_published_at = (
                current_project.published_at if current_project is not None else None
            )

            if data.get("published_at") is None:
                data["published_at"] = existing_published_at or datetime.now(UTC)

            return

        if status == "draft":
            data["is_featured"] = False

            if visibility == "public":
                data["visibility"] = "private"

            return

        if status == "archived":
            data["visibility"] = "private"
            data["is_featured"] = False

    @staticmethod
    def _extract_technology_assignments(
        data: dict[str, object],
    ) -> list[TechnologyAssignmentData]:
        """Remove and normalize technology assignments from schema data."""

        raw_assignments = data.pop(
            "technology_assignments",
            [],
        )

        if raw_assignments is None:
            return []

        if not isinstance(
            raw_assignments,
            list,
        ):
            return []

        normalized: list[TechnologyAssignmentData] = []
        seen_ids: set[UUID] = set()

        for fallback_sort_order, raw_assignment in enumerate(
            raw_assignments,
        ):
            if not isinstance(
                raw_assignment,
                dict,
            ):
                continue

            raw_technology_id = raw_assignment.get(
                "technology_id",
            )

            if raw_technology_id is None:
                continue

            technology_id = ProjectService._coerce_uuid(
                raw_technology_id,
            )

            if technology_id in seen_ids:
                continue

            raw_sort_order = raw_assignment.get(
                "sort_order",
                fallback_sort_order,
            )

            sort_order = (
                int(raw_sort_order)
                if raw_sort_order is not None
                else fallback_sort_order
            )

            normalized.append(
                TechnologyAssignmentData(
                    technology_id=technology_id,
                    is_featured=bool(
                        raw_assignment.get(
                            "is_featured",
                            False,
                        )
                    ),
                    sort_order=sort_order,
                )
            )

            seen_ids.add(
                technology_id,
            )

        return normalized

    @staticmethod
    def _normalize_project_dates(
        data: dict[str, object],
    ) -> None:
        """Convert JSON-serialized project datetimes back to datetime."""

        datetime_fields = (
            "started_at",
            "completed_at",
            "published_at",
        )

        for field_name in datetime_fields:
            value = data.get(
                field_name,
            )

            if value is None or isinstance(
                value,
                datetime,
            ):
                continue

            if isinstance(
                value,
                str,
            ):
                normalized_value = value.replace(
                    "Z",
                    "+00:00",
                )

                data[field_name] = datetime.fromisoformat(
                    normalized_value,
                )

    @staticmethod
    def _validate_publication_data(
        data: dict[str, object],
        category: ProjectCategory | None,
        *,
        current_project: Project | None = None,
    ) -> None:
        """Validate project data before creating or updating publication."""

        category_id = data.get(
            "category_id",
            (current_project.category_id if current_project is not None else None),
        )

        if category_id is None or category is None:
            raise ProjectPublicationError(
                "A project category is required before publication.",
            )

        title = str(
            data.get(
                "title",
                (current_project.title if current_project is not None else ""),
            )
        ).strip()

        short_description = str(
            data.get(
                "short_description",
                (
                    current_project.short_description
                    if current_project is not None
                    else ""
                ),
            )
        ).strip()

        description = str(
            data.get(
                "description",
                (current_project.description if current_project is not None else ""),
            )
        ).strip()

        if not title:
            raise ProjectPublicationError(
                "A project title is required before publication.",
            )

        if not short_description:
            raise ProjectPublicationError(
                "A short description is required before publication.",
            )

        if not description:
            raise ProjectPublicationError(
                "A full description is required before publication.",
            )

    @staticmethod
    def _is_published_data(
        data: dict[str, object],
    ) -> bool:
        """Return whether new project data represents publication."""

        return (
            str(
                data.get(
                    "status",
                    "draft",
                )
            )
            .strip()
            .lower()
            == "published"
        )

    @staticmethod
    def _will_be_published(
        project: Project,
        data: dict[str, object],
    ) -> bool:
        """Return whether an update leaves the project published."""

        resulting_status = (
            str(
                data.get(
                    "status",
                    project.status,
                )
            )
            .strip()
            .lower()
        )

        return resulting_status == "published"

    @staticmethod
    def _coerce_uuid(
        value: object,
    ) -> UUID:
        """Convert a serialized UUID value to UUID."""

        if isinstance(
            value,
            UUID,
        ):
            return value

        return UUID(
            str(value),
        )

    @staticmethod
    def _coerce_optional_uuid(
        value: object,
    ) -> UUID | None:
        """Convert an optional serialized UUID value to UUID."""

        if value is None:
            return None

        return ProjectService._coerce_uuid(
            value,
        )

    @staticmethod
    def _normalize_title(
        value: str,
    ) -> str:
        """Normalize whitespace in a project title."""

        return " ".join(
            value.split(),
        )

    @staticmethod
    def _normalize_slug(
        value: str,
    ) -> str:
        """Normalize a project slug."""

        return value.strip().lower()

    @staticmethod
    def _normalize_value(
        value: str,
    ) -> str:
        """Normalize a required lowercase value."""

        return value.strip().lower()

    @staticmethod
    def _normalize_optional_value(
        value: str | None,
    ) -> str | None:
        """Normalize an optional lowercase filter value."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        return normalized_value or None

    @staticmethod
    def _normalize_optional_slug(
        value: str | None,
    ) -> str | None:
        """Normalize an optional slug filter."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        return normalized_value or None


project_service = ProjectService(
    project_repository,
    project_category_repository,
    project_technology_repository,
)
