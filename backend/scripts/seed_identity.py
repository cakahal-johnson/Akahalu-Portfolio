import argparse
import asyncio
import getpass
import selectors
import sys
from dataclasses import dataclass

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.db.session import async_session_factory
from app.models.permission import Permission
from app.services.identity_service import identity_service


PERMISSIONS: tuple[
    tuple[str, str, str],
    ...,
] = (
    (
        "projects.read",
        "Read projects",
        "View project records and case studies.",
    ),
    (
        "projects.create",
        "Create projects",
        "Create new portfolio projects.",
    ),
    (
        "projects.update",
        "Update projects",
        "Edit existing portfolio projects.",
    ),
    (
        "projects.delete",
        "Delete projects",
        "Archive or delete portfolio projects.",
    ),
    (
        "blog.read",
        "Read blog posts",
        "View blog posts and drafts.",
    ),
    (
        "blog.create",
        "Create blog posts",
        "Create new blog posts.",
    ),
    (
        "blog.update",
        "Update blog posts",
        "Edit existing blog posts.",
    ),
    (
        "blog.delete",
        "Delete blog posts",
        "Archive or delete blog posts.",
    ),
    (
        "users.read",
        "Read users",
        "View administrative user accounts.",
    ),
    (
        "users.manage",
        "Manage users",
        "Create, update, suspend, and assign roles.",
    ),
    (
        "roles.manage",
        "Manage roles",
        "Manage roles and permission assignments.",
    ),
    (
        "messages.read",
        "Read contact messages",
        "View messages submitted through the website.",
    ),
    (
        "messages.manage",
        "Manage contact messages",
        "Update, archive, and delete contact messages.",
    ),
    (
        "settings.manage",
        "Manage settings",
        "Manage site-wide application settings.",
    ),
)


@dataclass(frozen=True)
class AdministratorInput:
    email: str
    password: str
    first_name: str
    last_name: str


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Seed identity roles and permissions and optionally "
            "create the first super administrator."
        ),
    )

    parser.add_argument(
        "--skip-admin",
        action="store_true",
        help="Seed roles and permissions without creating an administrator.",
    )

    return parser.parse_args()


def collect_administrator_input() -> AdministratorInput:
    email_adapter = TypeAdapter(EmailStr)

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

    first_name = input(
        "First name: ",
    ).strip()

    last_name = input(
        "Last name: ",
    ).strip()

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


async def seed_identity(
    administrator: AdministratorInput | None,
) -> None:
    async with async_session_factory() as session:
        try:
            permission_objects: list[Permission] = []

            for code, name, description in PERMISSIONS:
                permission = await identity_service.ensure_permission(
                    session,
                    code=code,
                    name=name,
                    description=description,
                )

                permission_objects.append(permission)

            await session.flush()

            super_admin_role = await identity_service.ensure_role(
                session,
                name="super_admin",
                display_name="Super Administrator",
                description=(
                    "Full access to all administrative features and settings."
                ),
                is_system=True,
                permissions=permission_objects,
            )

            await identity_service.ensure_role(
                session,
                name="admin",
                display_name="Administrator",
                description=(
                    "Administrative access without direct "
                    "super-admin account management."
                ),
                is_system=True,
                permissions=[
                    permission
                    for permission in permission_objects
                    if permission.code
                    not in {
                        "roles.manage",
                        "settings.manage",
                    }
                ],
            )

            await identity_service.ensure_role(
                session,
                name="editor",
                display_name="Content Editor",
                description=("Create and manage projects and blog content."),
                is_system=True,
                permissions=[
                    permission
                    for permission in permission_objects
                    if permission.code.startswith(
                        ("projects.", "blog."),
                    )
                ],
            )

            await identity_service.ensure_role(
                session,
                name="viewer",
                display_name="Viewer",
                description="Read-only administrative access.",
                is_system=True,
                permissions=[
                    permission
                    for permission in permission_objects
                    if permission.code.endswith(".read")
                ],
            )

            administrator_created = False

            if administrator is not None:
                _, administrator_created = await identity_service.ensure_super_admin(
                    session,
                    email=administrator.email,
                    password=administrator.password,
                    first_name=administrator.first_name,
                    last_name=administrator.last_name,
                    super_admin_role=super_admin_role,
                )

            await session.commit()

            print(f"Seeded {len(permission_objects)} permissions.")
            print("Seeded roles: super_admin, admin, editor, viewer.")

            if administrator is not None:
                action = "created" if administrator_created else "updated"

                print(f"Super-admin account {action}: {administrator.email}")
        except Exception:
            await session.rollback()
            raise


def create_windows_selector_loop() -> asyncio.AbstractEventLoop:
    return asyncio.SelectorEventLoop(
        selectors.SelectSelector(),
    )


def main() -> None:
    arguments = parse_arguments()

    administrator = None if arguments.skip_admin else collect_administrator_input()

    if sys.platform == "win32":
        with asyncio.Runner(
            loop_factory=create_windows_selector_loop,
        ) as runner:
            runner.run(
                seed_identity(administrator),
            )

        return

    asyncio.run(
        seed_identity(administrator),
    )


if __name__ == "__main__":
    main()
