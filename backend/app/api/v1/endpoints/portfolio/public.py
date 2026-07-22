from math import ceil
from typing import Annotated, NoReturn

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.schemas.portfolio import (
    ProjectCategoryRead,
    ProjectListResponse,
    ProjectRead,
    ProjectSummary,
    ProjectTechnologyCategory,
    ProjectTechnologyRead,
)
from app.services.portfolio import (
    ProjectCategoryNotFoundError,
    ProjectNotFoundError,
    ProjectTechnologyNotFoundError,
    project_category_service,
    project_service,
    project_technology_service,
)


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


PageQuery = Annotated[
    int,
    Query(
        ge=1,
        description="Page number to return.",
    ),
]


PageSizeQuery = Annotated[
    int,
    Query(
        ge=1,
        le=100,
        description="Number of projects to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=("Search project titles, descriptions and related content."),
    ),
]


CategorySlugQuery = Annotated[
    str | None,
    Query(
        min_length=2,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Filter projects by category slug.",
    ),
]


TechnologySlugQuery = Annotated[
    str | None,
    Query(
        min_length=2,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Filter projects by technology slug.",
    ),
]


FeaturedQuery = Annotated[
    bool | None,
    Query(
        description="Filter projects by featured status.",
    ),
]


def raise_public_not_found(
    *,
    code: str,
    message: str,
) -> NoReturn:
    """Raise a consistent public portfolio 404 response."""

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": code,
            "message": message,
        },
    )


@router.get(
    "/categories",
    response_model=list[ProjectCategoryRead],
    status_code=status.HTTP_200_OK,
    summary="List public portfolio categories",
)
async def list_public_categories(
    session: DatabaseSession,
) -> list[ProjectCategoryRead]:
    """
    Return active and non-deleted portfolio categories.

    Categories are returned according to their configured display order.
    """

    categories = await project_category_service.list_public(
        session,
    )

    return [
        ProjectCategoryRead.model_validate(
            category,
        )
        for category in categories
    ]


@router.get(
    "/categories/{slug}",
    response_model=ProjectCategoryRead,
    status_code=status.HTTP_200_OK,
    summary="Get a public portfolio category",
)
async def get_public_category(
    slug: str,
    session: DatabaseSession,
) -> ProjectCategoryRead:
    """Return an active portfolio category by slug."""

    try:
        category = await project_category_service.get_by_slug(
            session,
            slug,
        )
    except ProjectCategoryNotFoundError:
        raise_public_not_found(
            code="project_category_not_found",
            message="Portfolio category was not found.",
        )

    if not category.is_active or category.deleted_at is not None:
        raise_public_not_found(
            code="project_category_not_found",
            message="Portfolio category was not found.",
        )

    return ProjectCategoryRead.model_validate(
        category,
    )


@router.get(
    "/technologies",
    response_model=list[ProjectTechnologyRead],
    status_code=status.HTTP_200_OK,
    summary="List public portfolio technologies",
)
async def list_public_technologies(
    session: DatabaseSession,
    category: Annotated[
        ProjectTechnologyCategory | None,
        Query(
            description=("Filter technologies by their technology category."),
        ),
    ] = None,
) -> list[ProjectTechnologyRead]:
    """
    Return active and non-deleted portfolio technologies.

    Results may be filtered by a technology category such as language,
    framework, database, cloud, testing or tooling.
    """

    technologies = await project_technology_service.list_public(
        session,
        category=(category.value if category is not None else None),
    )

    return [
        ProjectTechnologyRead.model_validate(
            technology,
        )
        for technology in technologies
    ]


@router.get(
    "/technologies/{slug}",
    response_model=ProjectTechnologyRead,
    status_code=status.HTTP_200_OK,
    summary="Get a public portfolio technology",
)
async def get_public_technology(
    slug: str,
    session: DatabaseSession,
) -> ProjectTechnologyRead:
    """Return an active portfolio technology by slug."""

    try:
        technology = await project_technology_service.get_by_slug(
            session,
            slug,
        )
    except ProjectTechnologyNotFoundError:
        raise_public_not_found(
            code="project_technology_not_found",
            message="Portfolio technology was not found.",
        )

    if not technology.is_active or technology.deleted_at is not None:
        raise_public_not_found(
            code="project_technology_not_found",
            message="Portfolio technology was not found.",
        )

    return ProjectTechnologyRead.model_validate(
        technology,
    )


@router.get(
    "/projects",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List public portfolio projects",
)
async def list_public_projects(
    session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    category_slug: CategorySlugQuery = None,
    technology_slug: TechnologySlugQuery = None,
    is_featured: FeaturedQuery = None,
) -> ProjectListResponse:
    """
    Return paginated public portfolio projects.

    Only projects that are published, publicly visible, not deleted and
    have a publication timestamp are included.
    """

    offset = (page - 1) * page_size

    projects, total_items = await project_service.list_public(
        session,
        offset=offset,
        limit=page_size,
        search=search,
        category_id=None,
        category_slug=category_slug,
        technology_id=None,
        technology_slug=technology_slug,
        is_featured=is_featured,
    )

    total_pages = (
        ceil(
            total_items / page_size,
        )
        if total_items > 0
        else 0
    )

    return ProjectListResponse(
        items=[
            ProjectSummary.model_validate(
                project,
            )
            for project in projects
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/projects/featured",
    response_model=list[ProjectSummary],
    status_code=status.HTTP_200_OK,
    summary="List featured portfolio projects",
)
async def list_featured_projects(
    session: DatabaseSession,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=20,
            description=("Maximum number of featured projects to return."),
        ),
    ] = 6,
) -> list[ProjectSummary]:
    """Return a limited selection of featured public projects."""

    projects = await project_service.list_featured(
        session,
        limit=limit,
    )

    return [
        ProjectSummary.model_validate(
            project,
        )
        for project in projects
    ]


@router.get(
    "/projects/{slug}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Get a public portfolio project",
)
async def get_public_project(
    slug: str,
    session: DatabaseSession,
) -> ProjectRead:
    """Return a complete public portfolio project by slug."""

    try:
        project = await project_service.get_public_by_slug(
            session,
            slug,
        )
    except ProjectNotFoundError:
        raise_public_not_found(
            code="project_not_found",
            message="Published portfolio project was not found.",
        )

    return ProjectRead.model_validate(
        project,
    )
