import argparse
import asyncio
import selectors
import sys
from dataclasses import dataclass

from pydantic import EmailStr, TypeAdapter, ValidationError

import app.db.model_registry  # noqa: F401
from app.db.session import async_session_factory
from app.schemas.portfolio.profile import (
    ProfileAvailabilityStatus,
    ProfileCreate,
    ProfileUpdate,
)
from app.services.portfolio.profile_service import (
    ProfileNotFoundError,
    profile_service,
)


@dataclass(frozen=True, slots=True)
class PortfolioSeedInput:
    primary_email: str
    is_public: bool
    years_of_experience: int


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Seed or update the local portfolio profile "
            "using the application service layer."
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


def build_create_payload(
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


def build_update_payload(
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


async def seed_portfolio(
    seed_input: PortfolioSeedInput,
) -> None:
    async with async_session_factory() as session:
        try:
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
                    build_create_payload(
                        seed_input,
                    ),
                )

                action = "created"
            else:
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
                    build_update_payload(
                        seed_input,
                    ),
                )

                if profile.is_public != seed_input.is_public:
                    profile = await profile_service.set_visibility(
                        session,
                        is_public=(seed_input.is_public),
                    )

            await session.commit()
            await session.refresh(
                profile,
            )

            print()
            print(f"Portfolio profile {action}.")
            print(f"ID: {profile.id}")
            print(f"Display name: {profile.display_name}")
            print(f"Professional title: {profile.professional_title}")
            print(f"Public email: {profile.primary_email}")
            print(f"Public: {profile.is_public}")
            print(f"Deleted: {profile.deleted_at is not None}")
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
