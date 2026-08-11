import argparse
import asyncio
import getpass
import selectors
import sys
from dataclasses import dataclass

from pydantic import (
    EmailStr,
    TypeAdapter,
    ValidationError,
)

import app.db.model_registry  # noqa: F401
from app.db.session import async_session_factory
from app.models.permission import Permission
from app.services.identity_service import identity_service


PermissionSeed = tuple[
    str,
    str,
    str,
]


PERMISSIONS: tuple[
    PermissionSeed,
    ...,
] = (
    # =========================================================
    # Portfolio projects, categories, technologies,
    # links, and media
    # =========================================================
    (
        "projects.read",
        "Read projects",
        ("View portfolio projects, categories, technologies, links, and media."),
    ),
    (
        "projects.create",
        "Create projects",
        ("Create portfolio projects, categories, technologies, links, and media."),
    ),
    (
        "projects.update",
        "Update projects",
        (
            "Update portfolio projects, categories, "
            "technologies, links, media, visibility, "
            "featured state, and lifecycle status."
        ),
    ),
    (
        "projects.delete",
        "Delete projects",
        (
            "Delete, archive, restore, or otherwise "
            "manage destructive portfolio project operations."
        ),
    ),
    # =========================================================
    # Portfolio profile
    # =========================================================
    (
        "profile.read",
        "Read portfolio profile",
        ("View the administrative portfolio profile."),
    ),
    (
        "profile.create",
        "Create portfolio profile",
        ("Create the primary portfolio profile."),
    ),
    (
        "profile.update",
        "Update portfolio profile",
        (
            "Update portfolio profile content, visibility, "
            "availability, contact details, and SEO data."
        ),
    ),
    (
        "profile.delete",
        "Delete portfolio profile",
        ("Delete or restore the portfolio profile."),
    ),
    # =========================================================
    # Professional experience
    # =========================================================
    (
        "experience.read",
        "Read experience",
        ("View professional experience records."),
    ),
    (
        "experience.create",
        "Create experience",
        ("Create professional experience records."),
    ),
    (
        "experience.update",
        "Update experience",
        ("Update professional experience records, visibility, and featured state."),
    ),
    (
        "experience.delete",
        "Delete experience",
        ("Delete or restore professional experience records."),
    ),
    # =========================================================
    # Contact inquiries
    # =========================================================
    (
        "contact_inquiries.read",
        "Read contact inquiries",
        ("View contact inquiries submitted through the public portfolio."),
    ),
    (
        "contact_inquiries.update",
        "Update contact inquiries",
        (
            "Update inquiry workflow state, read state, "
            "priority, assignment, and internal details."
        ),
    ),
    (
        "contact_inquiries.delete",
        "Delete contact inquiries",
        ("Delete or restore contact inquiries."),
    ),
    # =========================================================
    # User administration
    # =========================================================
    (
        "users.manage",
        "Manage users",
        ("View and manage administrative user account lifecycle operations."),
    ),
    # =========================================================
    # RBAC administration
    # =========================================================
    (
        "roles.manage",
        "Manage roles",
        ("Manage roles, permissions, and user-role assignments."),
    ),
)


PERMISSION_CODES = frozenset(code for code, _, _ in PERMISSIONS)


ADMIN_PERMISSION_CODES = frozenset(
    code for code in PERMISSION_CODES if code != "roles.manage"
)


EDITOR_PERMISSION_CODES = frozenset(
    {
        "projects.read",
        "projects.create",
        "projects.update",
        "projects.delete",
        "profile.read",
        "profile.update",
        "experience.read",
        "experience.create",
        "experience.update",
        "experience.delete",
    }
)


VIEWER_PERMISSION_CODES = frozenset(
    code for code in PERMISSION_CODES if code.endswith(".read")
)


@dataclass(
    frozen=True,
    slots=True,
)
class AdministratorInput:
    email: str
    password: str
    first_name: str
    last_name: str


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize identity permissions and system "
            "roles and optionally create or recover the "
            "first super administrator."
        ),
    )

    parser.add_argument(
        "--skip-admin",
        action="store_true",
        help=(
            "Synchronize permissions and roles without prompting for an administrator."
        ),
    )

    return parser.parse_args()


def collect_administrator_input() -> AdministratorInput:
    email_adapter = TypeAdapter(
        EmailStr,
    )

    while True:
        raw_email = input(
            "Super-admin email: ",
        ).strip()

        try:
            email = str(
                email_adapter.validate_python(
                    raw_email,
                )
            ).lower()

            break
        except ValidationError:
            print("Enter a valid email address.")

    while True:
        first_name = input(
            "First name: ",
        ).strip()

        if first_name:
            break

        print("First name is required.")

    while True:
        last_name = input(
            "Last name: ",
        ).strip()

        if last_name:
            break

        print("Last name is required.")

    while True:
        password = getpass.getpass(
            "Password (minimum 12 characters): ",
        )

        password_confirmation = getpass.getpass(
            "Confirm password: ",
        )

        if len(password) < 12:
            print("Password must contain at least 12 characters.")

            continue

        if password != password_confirmation:
            print("Passwords do not match.")

            continue

        break

    return AdministratorInput(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def select_permissions(
    permissions: list[Permission],
    allowed_codes: frozenset[str],
) -> list[Permission]:
    return [
        permission for permission in permissions if (permission.code in allowed_codes)
    ]


async def seed_identity(
    administrator: AdministratorInput | None,
) -> None:
    async with async_session_factory() as session:
        try:
            permission_objects: list[Permission] = []

            for (
                code,
                name,
                description,
            ) in PERMISSIONS:
                permission = await identity_service.ensure_permission(
                    session,
                    code=code,
                    name=name,
                    description=(description),
                )

                permission_objects.append(permission)

            await session.flush()

            super_admin_role = await identity_service.ensure_role(
                session,
                name=("super_admin"),
                display_name=("Super Administrator"),
                description=("Full access to all administrative features and RBAC."),
                is_system=True,
                permissions=(permission_objects),
            )

            await identity_service.ensure_role(
                session,
                name="admin",
                display_name=("Administrator"),
                description=(
                    "Administrative access "
                    "to portfolio content, "
                    "inquiries, and user "
                    "lifecycle operations "
                    "without RBAC management."
                ),
                is_system=True,
                permissions=(
                    select_permissions(
                        permission_objects,
                        ADMIN_PERMISSION_CODES,
                    )
                ),
            )

            await identity_service.ensure_role(
                session,
                name="editor",
                display_name=("Content Editor"),
                description=(
                    "Create and manage "
                    "portfolio projects, "
                    "profile content, and "
                    "professional experience."
                ),
                is_system=True,
                permissions=(
                    select_permissions(
                        permission_objects,
                        EDITOR_PERMISSION_CODES,
                    )
                ),
            )

            await identity_service.ensure_role(
                session,
                name="viewer",
                display_name="Viewer",
                description=(
                    "Read-only access to "
                    "administrative portfolio "
                    "content and inquiries."
                ),
                is_system=True,
                permissions=(
                    select_permissions(
                        permission_objects,
                        VIEWER_PERMISSION_CODES,
                    )
                ),
            )

            administrator_created = False

            if administrator is not None:
                (
                    _,
                    administrator_created,
                ) = await identity_service.ensure_super_admin(
                    session,
                    email=(administrator.email),
                    password=(administrator.password),
                    first_name=(administrator.first_name),
                    last_name=(administrator.last_name),
                    super_admin_role=(super_admin_role),
                )

            await session.commit()

            print("Identity bootstrap completed successfully.")

            print((f"Synchronized {len(permission_objects)} permissions."))

            print(("Synchronized system roles: super_admin, admin, editor, viewer."))

            if administrator is not None:
                action = "created" if (administrator_created) else "updated"

                print((f"Super-admin account {action}: {administrator.email}"))

        except Exception:
            await session.rollback()

            raise


def create_windows_selector_loop() -> asyncio.AbstractEventLoop:
    return asyncio.SelectorEventLoop(
        selectors.SelectSelector(),
    )


def main() -> None:
    arguments = parse_arguments()

    administrator = None if (arguments.skip_admin) else (collect_administrator_input())

    if sys.platform == "win32":
        with asyncio.Runner(
            loop_factory=(create_windows_selector_loop),
        ) as runner:
            runner.run(seed_identity(administrator))

        return

    asyncio.run(seed_identity(administrator))


if __name__ == "__main__":
    main()
