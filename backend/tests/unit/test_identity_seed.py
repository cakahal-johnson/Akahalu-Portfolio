import ast
from pathlib import Path

from scripts.seed_identity import (
    ADMIN_PERMISSION_CODES,
    EDITOR_PERMISSION_CODES,
    PERMISSIONS,
    PERMISSION_CODES,
    VIEWER_PERMISSION_CODES,
)


BACKEND_DIR = Path(__file__).resolve().parents[2]

API_DIRECTORY = BACKEND_DIR / "app" / "api"

AUTHORIZED_DEPENDENCIES = {
    "require_permission",
    "require_any_permission",
}


def collect_required_api_permissions() -> set[str]:
    permission_codes: set[str] = set()

    for path in API_DIRECTORY.rglob("*.py"):
        tree = ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path),
        )

        for node in ast.walk(tree):
            if not isinstance(
                node,
                ast.Call,
            ):
                continue

            if not isinstance(
                node.func,
                ast.Name,
            ):
                continue

            if node.func.id not in (AUTHORIZED_DEPENDENCIES):
                continue

            for argument in node.args:
                if isinstance(
                    argument,
                    ast.Constant,
                ) and isinstance(
                    argument.value,
                    str,
                ):
                    permission_codes.add(argument.value)

    return permission_codes


def test_seed_permission_codes_are_unique() -> None:
    permission_codes = [
        code
        for (
            code,
            _,
            _,
        ) in PERMISSIONS
    ]

    assert len(permission_codes) == len(set(permission_codes))


def test_seed_covers_all_api_permissions() -> None:
    required_permissions = collect_required_api_permissions()

    assert required_permissions == PERMISSION_CODES


def test_retired_permissions_are_not_seeded() -> None:
    retired_permissions = {
        "blog.read",
        "blog.create",
        "blog.update",
        "blog.delete",
        "messages.read",
        "messages.manage",
        "settings.manage",
        "users.read",
    }

    assert PERMISSION_CODES.isdisjoint(retired_permissions)


def test_admin_role_excludes_rbac_management() -> None:
    assert "roles.manage" not in (ADMIN_PERMISSION_CODES)

    assert "users.manage" in (ADMIN_PERMISSION_CODES)

    assert "contact_inquiries.delete" in (ADMIN_PERMISSION_CODES)


def test_editor_role_contains_only_content_permissions() -> None:
    assert EDITOR_PERMISSION_CODES == {
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


def test_viewer_role_is_read_only() -> None:
    assert VIEWER_PERMISSION_CODES == {
        "projects.read",
        "profile.read",
        "experience.read",
        "contact_inquiries.read",
    }
