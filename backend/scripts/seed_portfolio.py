import argparse
import asyncio
import selectors
import sys
from dataclasses import dataclass

from pydantic import (
    EmailStr,
    TypeAdapter,
    ValidationError,
)
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.model_registry  # noqa: F401
from app.db.session import async_session_factory
from app.models.project import Project
from app.models.project_category import ProjectCategory
from app.models.project_technology import ProjectTechnology
from app.schemas.portfolio.common import (
    ProjectStatus,
    ProjectTechnologyCategory,
    ProjectVisibility,
    ResourceUrl,
)
from app.schemas.portfolio.profile import (
    ProfileAvailabilityStatus,
    ProfileCreate,
    ProfileUpdate,
)
from app.schemas.portfolio.project import (
    ProjectCreate,
    ProjectTechnologyAssignmentCreate,
    ProjectUpdate,
)
from app.schemas.portfolio.project_category import (
    ProjectCategoryCreate,
    ProjectCategoryUpdate,
)
from app.schemas.portfolio.project_technology import (
    ProjectTechnologyCreate,
    ProjectTechnologyUpdate,
)
from app.services.portfolio.profile_service import (
    ProfileNotFoundError,
    profile_service,
)
from app.services.portfolio.project_category_service import (
    ProjectCategoryNotFoundError,
    project_category_service,
)
from app.services.portfolio.project_service import (
    ProjectNotFoundError,
    project_service,
)
from app.services.portfolio.project_technology_service import (
    ProjectTechnologyNotFoundError,
    project_technology_service,
)


@dataclass(frozen=True, slots=True)
class PortfolioSeedInput:
    primary_email: str
    is_public: bool
    years_of_experience: int


@dataclass(frozen=True, slots=True)
class CategorySeed:
    name: str
    slug: str
    description: str
    icon: str
    sort_order: int
    seo_title: str
    seo_description: str


@dataclass(frozen=True, slots=True)
class TechnologySeed:
    name: str
    slug: str
    description: str
    category: ProjectTechnologyCategory
    icon: str
    sort_order: int


CATEGORY_SEEDS: tuple[
    CategorySeed,
    ...,
] = (
    CategorySeed(
        name="Full-Stack Development",
        slug="full-stack-development",
        description=(
            "Complete web applications combining modern frontend "
            "interfaces, backend APIs, databases, security, and "
            "production-oriented architecture."
        ),
        icon="layers",
        sort_order=1,
        seo_title="Full-Stack Development Projects",
        seo_description=(
            "Explore full-stack projects combining modern frontend, "
            "backend, database, security, and deployment technologies."
        ),
    ),
    CategorySeed(
        name="Backend & APIs",
        slug="backend-apis",
        description=(
            "Backend platforms, REST APIs, authentication systems, "
            "database services, and secure application infrastructure."
        ),
        icon="server",
        sort_order=2,
        seo_title="Backend and API Projects",
        seo_description=(
            "Explore backend and API projects focused on secure, "
            "scalable, tested, and maintainable application services."
        ),
    ),
    CategorySeed(
        name="Mobile Development",
        slug="mobile-development",
        description=(
            "Mobile and cross-platform application projects designed "
            "for reliable, responsive, and maintainable user experiences."
        ),
        icon="smartphone",
        sort_order=3,
        seo_title="Mobile Development Projects",
        seo_description=(
            "Explore mobile development projects built for modern "
            "Android and cross-platform application experiences."
        ),
    ),
)


TECHNOLOGY_SEEDS: tuple[
    TechnologySeed,
    ...,
] = (
    TechnologySeed(
        name="Python",
        slug="python",
        description=(
            "A general-purpose programming language used for backend "
            "services, automation, testing, and application development."
        ),
        category=ProjectTechnologyCategory.LANGUAGE,
        icon="python",
        sort_order=1,
    ),
    TechnologySeed(
        name="FastAPI",
        slug="fastapi",
        description=(
            "A modern Python framework used to build typed, high-performance web APIs."
        ),
        category=ProjectTechnologyCategory.FRAMEWORK,
        icon="fastapi",
        sort_order=2,
    ),
    TechnologySeed(
        name="PostgreSQL",
        slug="postgresql",
        description=(
            "A production-grade relational database used for structured "
            "application data and transactional workloads."
        ),
        category=ProjectTechnologyCategory.DATABASE,
        icon="postgresql",
        sort_order=3,
    ),
    TechnologySeed(
        name="Redis",
        slug="redis",
        description=(
            "An in-memory data platform used for caching, temporary "
            "application state, and high-performance workflows."
        ),
        category=ProjectTechnologyCategory.DATABASE,
        icon="redis",
        sort_order=4,
    ),
    TechnologySeed(
        name="Next.js",
        slug="nextjs",
        description=(
            "A React framework used to build server-rendered, "
            "SEO-friendly, and production-ready web applications."
        ),
        category=ProjectTechnologyCategory.FRAMEWORK,
        icon="nextjs",
        sort_order=5,
    ),
    TechnologySeed(
        name="TypeScript",
        slug="typescript",
        description=(
            "A typed JavaScript language used to improve frontend "
            "reliability, tooling, and maintainability."
        ),
        category=ProjectTechnologyCategory.LANGUAGE,
        icon="typescript",
        sort_order=6,
    ),
    TechnologySeed(
        name="React",
        slug="react",
        description=(
            "A component-based user interface library used for "
            "interactive web application experiences."
        ),
        category=ProjectTechnologyCategory.LIBRARY,
        icon="react",
        sort_order=7,
    ),
    TechnologySeed(
        name="Docker",
        slug="docker",
        description=(
            "A container platform used for reproducible development "
            "environments and application deployment."
        ),
        category=ProjectTechnologyCategory.DEVOPS,
        icon="docker",
        sort_order=8,
    ),
    TechnologySeed(
        name="Kotlin",
        slug="kotlin",
        description=(
            "A modern programming language used for Android and "
            "JVM-based application development."
        ),
        category=ProjectTechnologyCategory.LANGUAGE,
        icon="kotlin",
        sort_order=9,
    ),
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Seed or update development portfolio data using "
            "the application's service layer."
        ),
    )

    parser.add_argument(
        "--email",
        help=("Public portfolio email address. If omitted, the script prompts for it."),
    )

    parser.add_argument(
        "--private",
        action="store_true",
        help="Seed the profile as private instead of publicly visible.",
    )

    parser.add_argument(
        "--years-of-experience",
        type=int,
        default=0,
        help="Years of professional experience to publish. Defaults to 0.",
    )

    return parser.parse_args()


def validate_email(
    value: str,
) -> str:
    email_adapter = TypeAdapter(
        EmailStr,
    )

    try:
        return str(
            email_adapter.validate_python(
                value.strip(),
            )
        ).lower()
    except ValidationError as exc:
        raise ValueError(
            "A valid public email address is required.",
        ) from exc


def parse_resource_url(
    value: str,
) -> ResourceUrl:
    return TypeAdapter(
        ResourceUrl,
    ).validate_python(
        value,
    )


def collect_seed_input(
    arguments: argparse.Namespace,
) -> PortfolioSeedInput:
    raw_email = arguments.email

    if raw_email is None:
        raw_email = input(
            "Public portfolio email: ",
        ).strip()

    primary_email = validate_email(
        raw_email,
    )

    years_of_experience = int(
        arguments.years_of_experience,
    )

    if years_of_experience < 0:
        raise ValueError(
            "Years of experience cannot be negative.",
        )

    return PortfolioSeedInput(
        primary_email=primary_email,
        is_public=not arguments.private,
        years_of_experience=years_of_experience,
    )


def build_profile_create_payload(
    seed_input: PortfolioSeedInput,
) -> ProfileCreate:
    return ProfileCreate(
        first_name="Akahalu",
        middle_name="Chinonso",
        last_name="Vitalis",
        display_name="Akahalu Vitalis",
        professional_title=("Full-Stack Software Developer"),
        headline=("Building secure, scalable web APIs and modern digital products."),
        short_bio=(
            "Full-stack software developer focused on secure APIs, "
            "responsive web applications, database architecture, "
            "and mobile-ready software systems."
        ),
        biography=(
            "Akahalu Vitalis is a full-stack software developer "
            "focused on building secure, maintainable, and "
            "production-ready digital products. His work spans "
            "backend API development, modern web applications, "
            "mobile development, relational database design, "
            "authentication and authorization, automated testing, "
            "and deployment-oriented architecture. He works "
            "primarily with Python, FastAPI, PostgreSQL, Next.js, "
            "TypeScript, JavaScript, Kotlin, Java, PHP, Redis, "
            "and modern software engineering practices."
        ),
        location="Regina, Saskatchewan",
        country="Canada",
        timezone="America/Regina",
        primary_email=seed_input.primary_email,
        phone=None,
        website_url=None,
        resume_url=None,
        profile_image_url=None,
        years_of_experience=(seed_input.years_of_experience),
        availability_status=(ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES),
        availability_message=(
            "Open to software development opportunities, "
            "collaborations, and technically challenging projects."
        ),
        is_public=seed_input.is_public,
        seo_title=("Akahalu Vitalis | Full-Stack Software Developer"),
        seo_description=(
            "Portfolio of Akahalu Vitalis, a full-stack software "
            "developer specializing in secure APIs, modern web "
            "applications, databases, and mobile-ready software."
        ),
    )


def build_profile_update_payload(
    seed_input: PortfolioSeedInput,
) -> ProfileUpdate:
    return ProfileUpdate(
        first_name="Akahalu",
        middle_name="Chinonso",
        last_name="Vitalis",
        display_name="Akahalu Vitalis",
        professional_title=("Full-Stack Software Developer"),
        headline=("Building secure, scalable web APIs and modern digital products."),
        short_bio=(
            "Full-stack software developer focused on secure APIs, "
            "responsive web applications, database architecture, "
            "and mobile-ready software systems."
        ),
        biography=(
            "Akahalu Vitalis is a full-stack software developer "
            "focused on building secure, maintainable, and "
            "production-ready digital products. His work spans "
            "backend API development, modern web applications, "
            "mobile development, relational database design, "
            "authentication and authorization, automated testing, "
            "and deployment-oriented architecture. He works "
            "primarily with Python, FastAPI, PostgreSQL, Next.js, "
            "TypeScript, JavaScript, Kotlin, Java, PHP, Redis, "
            "and modern software engineering practices."
        ),
        location="Regina, Saskatchewan",
        country="Canada",
        timezone="America/Regina",
        primary_email=seed_input.primary_email,
        phone=None,
        website_url=None,
        resume_url=None,
        profile_image_url=None,
        years_of_experience=(seed_input.years_of_experience),
        availability_status=(ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES),
        availability_message=(
            "Open to software development opportunities, "
            "collaborations, and technically challenging projects."
        ),
        seo_title=("Akahalu Vitalis | Full-Stack Software Developer"),
        seo_description=(
            "Portfolio of Akahalu Vitalis, a full-stack software "
            "developer specializing in secure APIs, modern web "
            "applications, databases, and mobile-ready software."
        ),
    )


async def seed_profile(
    session: AsyncSession,
    seed_input: PortfolioSeedInput,
) -> str:
    try:
        existing_profile = await profile_service.get_admin(
            session,
            include_deleted=True,
        )
    except ProfileNotFoundError:
        existing_profile = None

    if existing_profile is None:
        profile = await profile_service.create(
            session,
            build_profile_create_payload(
                seed_input,
            ),
        )

        return f"created ({profile.display_name})"

    if existing_profile.deleted_at is not None:
        await profile_service.restore(
            session,
            restore_as_public=(seed_input.is_public),
        )

        action = "restored and updated"
    else:
        action = "updated"

    profile = await profile_service.update(
        session,
        build_profile_update_payload(
            seed_input,
        ),
    )

    if profile.is_public != seed_input.is_public:
        await profile_service.set_visibility(
            session,
            is_public=(seed_input.is_public),
        )

    return f"{action} ({profile.display_name})"


async def ensure_category(
    session: AsyncSession,
    seed: CategorySeed,
) -> ProjectCategory:
    try:
        category = await project_category_service.get_by_slug(
            session,
            seed.slug,
            include_deleted=True,
        )
    except ProjectCategoryNotFoundError:
        return await project_category_service.create(
            session,
            ProjectCategoryCreate(
                name=seed.name,
                slug=seed.slug,
                description=seed.description,
                icon=seed.icon,
                color=None,
                is_active=True,
                sort_order=seed.sort_order,
                seo_title=seed.seo_title,
                seo_description=(seed.seo_description),
            ),
        )

    if category.deleted_at is not None:
        category = await project_category_service.restore(
            session,
            category.id,
        )

    category = await project_category_service.update(
        session,
        category.id,
        ProjectCategoryUpdate(
            name=seed.name,
            slug=seed.slug,
            description=seed.description,
            icon=seed.icon,
            is_active=True,
            sort_order=seed.sort_order,
            seo_title=seed.seo_title,
            seo_description=(seed.seo_description),
        ),
    )

    if not category.is_active:
        category = await project_category_service.set_active(
            session,
            category.id,
            is_active=True,
        )

    return category


async def seed_categories(
    session: AsyncSession,
) -> dict[str, ProjectCategory]:
    categories: dict[
        str,
        ProjectCategory,
    ] = {}

    for seed in CATEGORY_SEEDS:
        category = await ensure_category(
            session,
            seed,
        )

        categories[seed.slug] = category

    return categories


async def ensure_technology(
    session: AsyncSession,
    seed: TechnologySeed,
) -> ProjectTechnology:
    try:
        technology = await project_technology_service.get_by_slug(
            session,
            seed.slug,
            include_deleted=True,
        )
    except ProjectTechnologyNotFoundError:
        return await project_technology_service.create(
            session,
            ProjectTechnologyCreate(
                name=seed.name,
                slug=seed.slug,
                description=seed.description,
                category=seed.category,
                icon=seed.icon,
                official_url=None,
                color=None,
                is_active=True,
                sort_order=seed.sort_order,
            ),
        )

    if technology.deleted_at is not None:
        technology = await project_technology_service.restore(
            session,
            technology.id,
        )

    technology = await project_technology_service.update(
        session,
        technology.id,
        ProjectTechnologyUpdate(
            name=seed.name,
            slug=seed.slug,
            description=seed.description,
            category=seed.category,
            icon=seed.icon,
            is_active=True,
            sort_order=seed.sort_order,
        ),
    )

    if not technology.is_active:
        technology = await project_technology_service.set_active(
            session,
            technology.id,
            is_active=True,
        )

    return technology


async def seed_technologies(
    session: AsyncSession,
) -> dict[str, ProjectTechnology]:
    technologies: dict[
        str,
        ProjectTechnology,
    ] = {}

    for seed in TECHNOLOGY_SEEDS:
        technology = await ensure_technology(
            session,
            seed,
        )

        technologies[seed.slug] = technology

    return technologies


def build_project_assignments(
    technologies: dict[
        str,
        ProjectTechnology,
    ],
) -> list[ProjectTechnologyAssignmentCreate]:
    selected_slugs = (
        "python",
        "fastapi",
        "postgresql",
        "redis",
        "nextjs",
        "typescript",
        "react",
        "docker",
    )

    assignments: list[ProjectTechnologyAssignmentCreate] = []

    for sort_order, slug in enumerate(
        selected_slugs,
        start=1,
    ):
        technology = technologies[slug]

        assignments.append(
            ProjectTechnologyAssignmentCreate(
                technology_id=technology.id,
                is_featured=(sort_order <= 6),
                sort_order=sort_order,
            )
        )

    return assignments


def build_project_create_payload(
    category: ProjectCategory,
    technologies: dict[
        str,
        ProjectTechnology,
    ],
) -> ProjectCreate:
    return ProjectCreate(
        title="Akahalu Portfolio",
        slug="akahalu-portfolio",
        short_description=(
            "A production-ready full-stack portfolio platform "
            "built with FastAPI, PostgreSQL, Next.js, TypeScript, "
            "secure authentication, and tested administration."
        ),
        description=(
            "Akahalu Portfolio is a full-stack software platform "
            "designed to present professional projects, experience, "
            "technical capabilities, and contact information through "
            "a responsive public website backed by a secure "
            "administration API. The backend follows a layered "
            "FastAPI architecture with Pydantic schemas, service and "
            "repository boundaries, asynchronous SQLAlchemy, "
            "PostgreSQL persistence, authentication, session "
            "management, RBAC, soft deletion, lifecycle controls, "
            "and automated integration testing. The frontend uses "
            "Next.js, TypeScript, server rendering, responsive UI "
            "components, typed API contracts, and a reusable data "
            "access layer."
        ),
        problem_statement=(
            "A professional software portfolio needs more than a "
            "collection of static pages. Content must be structured, "
            "maintainable, securely administered, searchable, and "
            "capable of evolving as new projects and professional "
            "experience are added."
        ),
        solution_summary=(
            "The solution is a modular full-stack portfolio platform "
            "with a typed FastAPI backend, PostgreSQL data model, "
            "secure identity and authorization system, public content "
            "APIs, and a responsive Next.js frontend consuming those "
            "APIs through server-side and typed data services."
        ),
        key_features=(
            "- Secure authentication and session management\n"
            "- Role-based access control and superuser authorization\n"
            "- Public and administrative portfolio APIs\n"
            "- Project categories and technology relationships\n"
            "- Publication, featured, visibility, and soft-delete workflows\n"
            "- Contact inquiry management\n"
            "- Server-rendered public portfolio pages\n"
            "- Search, filtering, and pagination foundations\n"
            "- Responsive desktop and mobile navigation\n"
            "- Automated unit and integration testing"
        ),
        technical_highlights=(
            "- FastAPI with typed Pydantic request and response contracts\n"
            "- Async SQLAlchemy 2.x with PostgreSQL and Alembic migrations\n"
            "- Repository and service-layer separation\n"
            "- JWT access and refresh token workflows\n"
            "- Session revocation and account lifecycle controls\n"
            "- Next.js App Router with TypeScript and server rendering\n"
            "- Tailwind CSS and reusable UI components\n"
            "- TanStack Query foundation for interactive client data\n"
            "- Docker-based development infrastructure\n"
            "- Ruff, mypy, pytest, ESLint, TypeScript, and production builds"
        ),
        category_id=category.id,
        status=ProjectStatus.DRAFT,
        visibility=ProjectVisibility.PRIVATE,
        is_featured=False,
        sort_order=1,
        repository_url=parse_resource_url(
            "https://github.com/cakahal-johnson/Akahalu-Portfolio"
        ),
        live_url=None,
        case_study_url=None,
        thumbnail_url=None,
        started_at=None,
        completed_at=None,
        published_at=None,
        seo_title=("Akahalu Portfolio | Full-Stack Software Project"),
        seo_description=(
            "A production-ready portfolio platform built with FastAPI, "
            "PostgreSQL, Next.js, TypeScript, secure authentication, "
            "RBAC, and automated testing."
        ),
        technology_assignments=(
            build_project_assignments(
                technologies,
            )
        ),
    )


def build_project_update_payload(
    category: ProjectCategory,
    technologies: dict[
        str,
        ProjectTechnology,
    ],
) -> ProjectUpdate:
    return ProjectUpdate(
        title="Akahalu Portfolio",
        slug="akahalu-portfolio",
        short_description=(
            "A production-ready full-stack portfolio platform "
            "built with FastAPI, PostgreSQL, Next.js, TypeScript, "
            "secure authentication, and tested administration."
        ),
        description=(
            "Akahalu Portfolio is a full-stack software platform "
            "designed to present professional projects, experience, "
            "technical capabilities, and contact information through "
            "a responsive public website backed by a secure "
            "administration API. The backend follows a layered "
            "FastAPI architecture with Pydantic schemas, service and "
            "repository boundaries, asynchronous SQLAlchemy, "
            "PostgreSQL persistence, authentication, session "
            "management, RBAC, soft deletion, lifecycle controls, "
            "and automated integration testing. The frontend uses "
            "Next.js, TypeScript, server rendering, responsive UI "
            "components, typed API contracts, and a reusable data "
            "access layer."
        ),
        problem_statement=(
            "A professional software portfolio needs more than a "
            "collection of static pages. Content must be structured, "
            "maintainable, securely administered, searchable, and "
            "capable of evolving as new projects and professional "
            "experience are added."
        ),
        solution_summary=(
            "The solution is a modular full-stack portfolio platform "
            "with a typed FastAPI backend, PostgreSQL data model, "
            "secure identity and authorization system, public content "
            "APIs, and a responsive Next.js frontend consuming those "
            "APIs through server-side and typed data services."
        ),
        key_features=(
            "- Secure authentication and session management\n"
            "- Role-based access control and superuser authorization\n"
            "- Public and administrative portfolio APIs\n"
            "- Project categories and technology relationships\n"
            "- Publication, featured, visibility, and soft-delete workflows\n"
            "- Contact inquiry management\n"
            "- Server-rendered public portfolio pages\n"
            "- Search, filtering, and pagination foundations\n"
            "- Responsive desktop and mobile navigation\n"
            "- Automated unit and integration testing"
        ),
        technical_highlights=(
            "- FastAPI with typed Pydantic request and response contracts\n"
            "- Async SQLAlchemy 2.x with PostgreSQL and Alembic migrations\n"
            "- Repository and service-layer separation\n"
            "- JWT access and refresh token workflows\n"
            "- Session revocation and account lifecycle controls\n"
            "- Next.js App Router with TypeScript and server rendering\n"
            "- Tailwind CSS and reusable UI components\n"
            "- TanStack Query foundation for interactive client data\n"
            "- Docker-based development infrastructure\n"
            "- Ruff, mypy, pytest, ESLint, TypeScript, and production builds"
        ),
        category_id=category.id,
        sort_order=1,
        repository_url=parse_resource_url(
            "https://github.com/cakahal-johnson/Akahalu-Portfolio"
        ),
        live_url=None,
        case_study_url=None,
        thumbnail_url=None,
        seo_title=("Akahalu Portfolio | Full-Stack Software Project"),
        seo_description=(
            "A production-ready portfolio platform built with FastAPI, "
            "PostgreSQL, Next.js, TypeScript, secure authentication, "
            "RBAC, and automated testing."
        ),
        technology_assignments=(
            build_project_assignments(
                technologies,
            )
        ),
    )


async def seed_akahalu_portfolio_project(
    session: AsyncSession,
    *,
    category: ProjectCategory,
    technologies: dict[
        str,
        ProjectTechnology,
    ],
) -> Project:
    try:
        project = await project_service.get_by_slug(
            session,
            "akahalu-portfolio",
            include_deleted=True,
        )
    except ProjectNotFoundError:
        project = await project_service.create(
            session,
            build_project_create_payload(
                category,
                technologies,
            ),
        )
    else:
        if project.deleted_at is not None:
            project = await project_service.restore(
                session,
                project.id,
                restore_as_draft=True,
            )

        project = await project_service.update(
            session,
            project.id,
            build_project_update_payload(
                category,
                technologies,
            ),
        )

    project = await project_service.publish(
        session,
        project.id,
        visibility=(ProjectVisibility.PUBLIC.value),
    )

    if not project.is_featured:
        project = await project_service.set_featured(
            session,
            project.id,
            is_featured=True,
        )

    return project


async def seed_portfolio(
    seed_input: PortfolioSeedInput,
) -> None:
    async with async_session_factory() as session:
        try:
            profile_action = await seed_profile(
                session,
                seed_input,
            )

            categories = await seed_categories(
                session,
            )

            technologies = await seed_technologies(
                session,
            )

            project = await seed_akahalu_portfolio_project(
                session,
                category=categories["full-stack-development"],
                technologies=technologies,
            )

            await session.commit()

            print()
            print("Portfolio development data seeded successfully.")
            print()
            print(f"Profile: {profile_action}")
            print(f"Categories: {len(categories)}")
            print(f"Technologies: {len(technologies)}")
            print(f"Project: {project.title}")
            print(f"Project slug: {project.slug}")
            print(f"Project status: {project.status}")
            print(f"Project visibility: {project.visibility}")
            print(f"Project featured: {project.is_featured}")
        except Exception:
            await session.rollback()
            raise


def create_windows_selector_loop() -> asyncio.AbstractEventLoop:
    return asyncio.SelectorEventLoop(
        selectors.SelectSelector(),
    )


def main() -> None:
    arguments = parse_arguments()

    try:
        seed_input = collect_seed_input(
            arguments,
        )
    except ValueError as exc:
        raise SystemExit(
            str(exc),
        ) from exc

    if sys.platform == "win32":
        with asyncio.Runner(
            loop_factory=create_windows_selector_loop,
        ) as runner:
            runner.run(
                seed_portfolio(
                    seed_input,
                )
            )

        return

    asyncio.run(
        seed_portfolio(
            seed_input,
        )
    )


if __name__ == "__main__":
    main()
