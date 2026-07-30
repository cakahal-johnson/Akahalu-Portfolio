from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.schemas.portfolio.experience import (
    EmploymentType,
    ExperienceListResponse,
    ExperienceLocationType,
    ExperienceRead,
    ExperienceSummary,
)
from app.services.portfolio.experience_service import (
    ExperienceNotFoundError,
    experience_service,
)


router = APIRouter(
    prefix="/portfolio/experiences",
    tags=["Portfolio Experiences"],
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
        description="Number of experiences to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=(
            "Search experiences by company, job title, slug, location, "
            "summary, responsibilities, or achievements."
        ),
    ),
]


EmploymentTypeQuery = Annotated[
    EmploymentType | None,
    Query(
        description="Filter experiences by employment type.",
    ),
]


LocationTypeQuery = Annotated[
    ExperienceLocationType | None,
    Query(
        description="Filter experiences by work-location arrangement.",
    ),
]


CurrentQuery = Annotated[
    bool | None,
    Query(
        description="Filter experiences by current-position status.",
    ),
]


FeaturedQuery = Annotated[
    bool | None,
    Query(
        description="Filter experiences by featured status.",
    ),
]


FeaturedLimitQuery = Annotated[
    int,
    Query(
        ge=1,
        le=20,
        description="Maximum number of featured experiences to return.",
    ),
]


@router.get(
    "",
    response_model=ExperienceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List public portfolio experiences",
)
async def list_public_experiences(
    database_session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    employment_type: EmploymentTypeQuery = None,
    location_type: LocationTypeQuery = None,
    is_current: CurrentQuery = None,
    is_featured: FeaturedQuery = None,
) -> ExperienceListResponse:
    """Return paginated publicly visible portfolio experiences."""

    experiences, total_items = await experience_service.list_public(
        database_session,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
        employment_type=(
            employment_type.value if employment_type is not None else None
        ),
        location_type=(location_type.value if location_type is not None else None),
        is_current=is_current,
        is_featured=is_featured,
    )

    total_pages = (
        ceil(
            total_items / page_size,
        )
        if total_items > 0
        else 0
    )

    return ExperienceListResponse(
        items=[
            ExperienceSummary.model_validate(
                experience,
            )
            for experience in experiences
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/featured",
    response_model=list[ExperienceSummary],
    status_code=status.HTTP_200_OK,
    summary="List featured portfolio experiences",
)
async def list_featured_experiences(
    database_session: DatabaseSession,
    limit: FeaturedLimitQuery = 6,
) -> list[ExperienceSummary]:
    """Return featured publicly visible portfolio experiences."""

    experiences = await experience_service.list_featured(
        database_session,
        limit=limit,
    )

    return [
        ExperienceSummary.model_validate(
            experience,
        )
        for experience in experiences
    ]


@router.get(
    "/{slug}",
    response_model=ExperienceRead,
    status_code=status.HTTP_200_OK,
    summary="Get a public portfolio experience",
)
async def get_public_experience(
    slug: str,
    database_session: DatabaseSession,
) -> ExperienceRead:
    """Return a publicly visible portfolio experience by slug."""

    try:
        experience = await experience_service.get_public_by_slug(
            database_session,
            slug,
        )
    except ExperienceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "experience_not_found",
                "message": str(exc),
            },
        ) from exc

    return ExperienceRead.model_validate(
        experience,
    )
