from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.contact_inquiry import ContactInquiry
from app.models.permission import Permission
from app.models.project import Project
from app.models.project_category import ProjectCategory
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongContactInquiryPassword123!"

PUBLIC_CONTACT_URL = "/api/v1/contact/inquiries"
ADMIN_CONTACT_URL = "/api/v1/admin/contact/inquiries"

pytestmark = pytest.mark.asyncio


def create_permission(
    code: str,
) -> Permission:
    return Permission(
        code=code,
        name=code.replace(".", " ").title(),
        description=f"Permission for {code}.",
        is_active=True,
    )


def create_role(
    name: str,
    *,
    permissions: list[Permission] | None = None,
) -> Role:
    return Role(
        name=name,
        display_name=name.replace("_", " ").title(),
        description=f"Role for {name}.",
        is_system=False,
        is_active=True,
        permissions=permissions or [],
    )


def create_user(
    *,
    email: str,
    roles: list[Role] | None = None,
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    return User(
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        first_name="Contact",
        last_name="Administrator",
        display_name="Contact Administrator",
        is_active=is_active,
        is_verified=True,
        is_superuser=is_superuser,
        roles=roles or [],
    )


def create_category(
    *,
    name: str,
    slug: str,
) -> ProjectCategory:
    return ProjectCategory(
        name=name,
        slug=slug,
        description=f"{name} portfolio projects.",
        icon="folder",
        color="#2563EB",
        is_active=True,
        sort_order=1,
    )


def create_project(
    *,
    title: str,
    slug: str,
    category: ProjectCategory | None = None,
    status: str = "draft",
    visibility: str = "private",
    published_at: datetime | None = None,
    deleted_at: datetime | None = None,
    created_by: User | None = None,
) -> Project:
    return Project(
        title=title,
        slug=slug,
        short_description=(
            f"{title} is a professional portfolio project available for review."
        ),
        description=(
            f"{title} demonstrates production-ready architecture, secure APIs, "
            "database integration, and maintainable engineering."
        ),
        category=category,
        status=status,
        visibility=visibility,
        is_featured=False,
        sort_order=1,
        published_at=published_at,
        deleted_at=deleted_at,
        created_by=created_by,
        updated_by=created_by,
    )


def create_contact_inquiry(
    *,
    name: str,
    email: str,
    subject: str,
    message: str,
    inquiry_type: str = "general",
    status: str = "new",
    priority: str = "normal",
    is_read: bool = False,
    assigned_to: User | None = None,
    project: Project | None = None,
    internal_notes: str | None = None,
    company: str | None = None,
    phone: str | None = None,
    created_at: datetime | None = None,
    deleted_at: datetime | None = None,
) -> ContactInquiry:
    now = datetime.now(UTC)

    inquiry = ContactInquiry(
        name=name,
        email=email,
        phone=phone,
        company=company,
        subject=subject,
        message=message,
        inquiry_type=inquiry_type,
        status=status,
        priority=priority,
        is_read=is_read,
        read_at=now if is_read else None,
        responded_at=now if status == "responded" else None,
        closed_at=now if status == "closed" else None,
        assigned_to=assigned_to,
        project=project,
        internal_notes=internal_notes,
        consent_given=True,
        source_page="/contact",
        user_agent="contact-inquiry-integration-tests",
        ip_address_hash="a" * 64,
        submission_fingerprint=uuid4().hex + uuid4().hex,
        deleted_at=deleted_at,
    )

    if created_at is not None:
        inquiry.created_at = created_at
        inquiry.updated_at = created_at

    return inquiry


async def login_user(
    client: AsyncClient,
    *,
    email: str,
) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
            "device_name": "Contact inquiry integration test",
        },
        headers={
            "User-Agent": "contact-inquiry-integration-tests",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    tokens = cast(
        dict[str, Any],
        payload["tokens"],
    )

    return str(
        tokens["access_token"],
    )


def authorization_headers(
    access_token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


def valid_public_payload(
    *,
    email: str = "visitor@example.com",
    subject: str = "Portfolio development opportunity",
    message: str = (
        "I would like to discuss a professional full-stack development opportunity."
    ),
    project_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": "  Portfolio   Visitor  ",
        "email": f"  {email.upper()}  ",
        "phone": "  +234 800 123 4567  ",
        "company": "  Example   Technologies  ",
        "subject": f"  {subject}  ",
        "message": f"  {message}  ",
        "inquiry_type": "project",
        "consent_given": True,
        "source_page": "  /portfolio/contact  ",
        "website": "",
    }

    if project_id is not None:
        payload["project_id"] = project_id

    return payload


@pytest_asyncio.fixture
async def admin_contact_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    contact_read = create_permission(
        "contact_inquiries.read",
    )
    contact_update = create_permission(
        "contact_inquiries.update",
    )
    contact_delete = create_permission(
        "contact_inquiries.delete",
    )
    unrelated_permission = create_permission(
        "settings.manage",
    )

    reader_role = create_role(
        "contact_inquiry_reader",
        permissions=[
            contact_read,
        ],
    )
    updater_role = create_role(
        "contact_inquiry_updater",
        permissions=[
            contact_update,
        ],
    )
    deleter_role = create_role(
        "contact_inquiry_deleter",
        permissions=[
            contact_delete,
        ],
    )
    manager_role = create_role(
        "contact_inquiry_manager",
        permissions=[
            contact_read,
            contact_update,
            contact_delete,
        ],
    )
    outsider_role = create_role(
        "contact_inquiry_outsider",
        permissions=[
            unrelated_permission,
        ],
    )

    reader_user = create_user(
        email="contact-reader@example.com",
        roles=[
            reader_role,
        ],
    )
    updater_user = create_user(
        email="contact-updater@example.com",
        roles=[
            updater_role,
        ],
    )
    deleter_user = create_user(
        email="contact-deleter@example.com",
        roles=[
            deleter_role,
        ],
    )
    manager_user = create_user(
        email="contact-manager@example.com",
        roles=[
            manager_role,
        ],
    )
    outsider_user = create_user(
        email="contact-outsider@example.com",
        roles=[
            outsider_role,
        ],
    )
    assigned_user = create_user(
        email="contact-assignee@example.com",
    )
    alternate_assignee = create_user(
        email="alternate-contact-assignee@example.com",
    )
    inactive_assignee = create_user(
        email="inactive-contact-assignee@example.com",
        is_active=False,
    )
    superuser = create_user(
        email="contact-superuser@example.com",
        is_superuser=True,
    )

    category = create_category(
        name="Web Applications",
        slug="web-applications",
    )

    published_project = create_project(
        title="Published Portfolio Platform",
        slug="published-portfolio-platform",
        category=category,
        status="published",
        visibility="public",
        published_at=datetime(
            2026,
            7,
            1,
            12,
            0,
            tzinfo=UTC,
        ),
        created_by=manager_user,
    )
    draft_project = create_project(
        title="Draft Portfolio Platform",
        slug="draft-portfolio-platform",
        category=category,
        created_by=manager_user,
    )

    base_time = datetime(
        2026,
        7,
        20,
        12,
        0,
        tzinfo=UTC,
    )

    new_inquiry = create_contact_inquiry(
        name="Alice Johnson",
        email="alice@example.com",
        company="Alice Consulting",
        phone="+1 306 555 0101",
        subject="Freelance web application",
        message=("I need a secure web application for my growing consulting business."),
        inquiry_type="freelance",
        status="new",
        priority="urgent",
        project=published_project,
        internal_notes="Priority client from the Saskatchewan market.",
        created_at=base_time,
    )
    in_progress_inquiry = create_contact_inquiry(
        name="Brian Smith",
        email="brian@example.com",
        subject="Employment opportunity",
        message=(
            "Our engineering team would like to discuss a backend developer role."
        ),
        inquiry_type="employment",
        status="in_progress",
        priority="high",
        is_read=True,
        assigned_to=assigned_user,
        created_at=base_time + timedelta(hours=1),
    )
    responded_inquiry = create_contact_inquiry(
        name="Chidinma Okafor",
        email="chidinma@example.com",
        subject="Collaboration proposal",
        message=("I would like to collaborate on an educational technology platform."),
        inquiry_type="collaboration",
        status="responded",
        priority="normal",
        is_read=True,
        assigned_to=assigned_user,
        created_at=base_time + timedelta(hours=2),
    )
    closed_inquiry = create_contact_inquiry(
        name="David Williams",
        email="david@example.com",
        subject="Completed support request",
        message=(
            "Thank you for resolving the deployment support request successfully."
        ),
        inquiry_type="support",
        status="closed",
        priority="low",
        is_read=True,
        created_at=base_time + timedelta(hours=3),
    )
    spam_inquiry = create_contact_inquiry(
        name="Promotional Sender",
        email="promotion@example.com",
        subject="Unwanted promotional message",
        message=("This is an unsolicited promotional contact inquiry for testing."),
        inquiry_type="other",
        status="spam",
        priority="normal",
        is_read=True,
        created_at=base_time + timedelta(hours=4),
    )
    deleted_inquiry = create_contact_inquiry(
        name="Deleted Sender",
        email="deleted@example.com",
        subject="Deleted contact inquiry",
        message=("This contact inquiry has been soft-deleted for integration testing."),
        inquiry_type="general",
        status="new",
        priority="normal",
        deleted_at=datetime.now(UTC),
        created_at=base_time + timedelta(hours=5),
    )

    database_session.add_all(
        [
            contact_read,
            contact_update,
            contact_delete,
            unrelated_permission,
            reader_role,
            updater_role,
            deleter_role,
            manager_role,
            outsider_role,
            reader_user,
            updater_user,
            deleter_user,
            manager_user,
            outsider_user,
            assigned_user,
            alternate_assignee,
            inactive_assignee,
            superuser,
            category,
            published_project,
            draft_project,
            new_inquiry,
            in_progress_inquiry,
            responded_inquiry,
            closed_inquiry,
            spam_inquiry,
            deleted_inquiry,
        ]
    )

    await database_session.flush()

    yield {
        "reader_user": reader_user,
        "updater_user": updater_user,
        "deleter_user": deleter_user,
        "manager_user": manager_user,
        "outsider_user": outsider_user,
        "assigned_user": assigned_user,
        "alternate_assignee": alternate_assignee,
        "inactive_assignee": inactive_assignee,
        "superuser": superuser,
        "published_project": published_project,
        "draft_project": draft_project,
        "new_inquiry": new_inquiry,
        "in_progress_inquiry": in_progress_inquiry,
        "responded_inquiry": responded_inquiry,
        "closed_inquiry": closed_inquiry,
        "spam_inquiry": spam_inquiry,
        "deleted_inquiry": deleted_inquiry,
    }


async def count_contact_inquiries(
    database_session: AsyncSession,
) -> int:
    result = await database_session.execute(
        select(
            func.count(
                ContactInquiry.id,
            )
        )
    )

    return result.scalar_one()


async def test_public_submission_succeeds_and_normalizes_values(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    response = await client.post(
        PUBLIC_CONTACT_URL,
        json=valid_public_payload(),
        headers={
            "User-Agent": "  Portfolio   Browser   Test  ",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json() == {
        "message": "Your message has been received successfully.",
    }

    result = await database_session.execute(
        select(
            ContactInquiry,
        ).where(
            ContactInquiry.email == "visitor@example.com",
        )
    )

    inquiry = result.scalar_one()

    assert inquiry.name == "Portfolio Visitor"
    assert inquiry.email == "visitor@example.com"
    assert inquiry.phone == "+234 800 123 4567"
    assert inquiry.company == "Example Technologies"
    assert inquiry.subject == "Portfolio development opportunity"
    assert inquiry.message == (
        "I would like to discuss a professional full-stack development opportunity."
    )
    assert inquiry.inquiry_type == "project"
    assert inquiry.status == "new"
    assert inquiry.priority == "normal"
    assert inquiry.is_read is False
    assert inquiry.read_at is None
    assert inquiry.consent_given is True
    assert inquiry.source_page == "/portfolio/contact"
    assert inquiry.user_agent == "Portfolio Browser Test"
    assert inquiry.ip_address_hash is not None
    assert len(inquiry.ip_address_hash) == 64
    assert inquiry.submission_fingerprint is not None
    assert len(inquiry.submission_fingerprint) == 64


async def test_public_submission_accepts_published_project(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_contact_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_contact_records["published_project"],
    )

    response = await client.post(
        PUBLIC_CONTACT_URL,
        json=valid_public_payload(
            email="project-visitor@example.com",
            project_id=str(project.id),
        ),
    )

    assert response.status_code == 201, response.text

    result = await database_session.execute(
        select(
            ContactInquiry,
        ).where(
            ContactInquiry.email == "project-visitor@example.com",
        )
    )

    inquiry = result.scalar_one()

    assert inquiry.project_id == project.id


async def test_public_submission_rejects_unavailable_project(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_contact_records["draft_project"],
    )

    response = await client.post(
        PUBLIC_CONTACT_URL,
        json=valid_public_payload(
            email="draft-project-visitor@example.com",
            project_id=str(project.id),
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == ("contact_inquiry_project_not_found")


async def test_public_honeypot_submission_is_masked(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    before_count = await count_contact_inquiries(
        database_session,
    )

    payload = valid_public_payload(
        email="honeypot@example.com",
    )
    payload["website"] = "https://spam.example.com"

    response = await client.post(
        PUBLIC_CONTACT_URL,
        json=payload,
    )

    after_count = await count_contact_inquiries(
        database_session,
    )

    assert response.status_code == 201, response.text
    assert response.json() == {
        "message": "Your message has been received successfully.",
    }
    assert after_count == before_count


async def test_public_duplicate_submission_is_masked(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    payload = valid_public_payload(
        email="duplicate@example.com",
    )

    first_response = await client.post(
        PUBLIC_CONTACT_URL,
        json=payload,
    )
    second_response = await client.post(
        PUBLIC_CONTACT_URL,
        json=payload,
    )

    result = await database_session.execute(
        select(
            func.count(
                ContactInquiry.id,
            )
        ).where(
            ContactInquiry.email == "duplicate@example.com",
        )
    )

    assert first_response.status_code == 201, first_response.text
    assert second_response.status_code == 201, second_response.text
    assert first_response.json() == second_response.json()
    assert result.scalar_one() == 1


async def test_public_submission_truncates_long_user_agent(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    long_user_agent = "A" * (settings.contact_user_agent_max_length + 200)

    response = await client.post(
        PUBLIC_CONTACT_URL,
        json=valid_public_payload(
            email="long-user-agent@example.com",
        ),
        headers={
            "User-Agent": long_user_agent,
        },
    )

    assert response.status_code == 201, response.text

    result = await database_session.execute(
        select(
            ContactInquiry,
        ).where(
            ContactInquiry.email == "long-user-agent@example.com",
        )
    )

    inquiry = result.scalar_one()

    assert inquiry.user_agent is not None
    assert len(inquiry.user_agent) == (settings.contact_user_agent_max_length)


async def test_list_inquiries_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get(
        ADMIN_CONTACT_URL,
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == ("invalid_authentication")


async def test_list_inquiries_rejects_missing_permission(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    user = cast(
        User,
        admin_contact_records["outsider_user"],
    )

    token = await login_user(
        client,
        email=user.email,
    )

    response = await client.get(
        ADMIN_CONTACT_URL,
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_list_inquiries_returns_paginated_results(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    user = cast(
        User,
        admin_contact_records["reader_user"],
    )

    token = await login_user(
        client,
        email=user.email,
    )

    response = await client.get(
        ADMIN_CONTACT_URL,
        params={
            "page": 1,
            "page_size": 2,
            "sort_by": "created_at",
            "sort_direction": "asc",
        },
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = response.json()

    assert payload["total_items"] == 5
    assert payload["total_pages"] == 3
    assert payload["has_next_page"] is True
    assert [item["email"] for item in payload["items"]] == [
        "alice@example.com",
        "brian@example.com",
    ]


@pytest.mark.parametrize(
    ("params", "expected_email"),
    [
        (
            {"search": "Saskatchewan market"},
            "alice@example.com",
        ),
        (
            {"inquiry_type": "employment"},
            "brian@example.com",
        ),
        (
            {"inquiry_status": "responded"},
            "chidinma@example.com",
        ),
        (
            {"priority": "low"},
            "david@example.com",
        ),
        (
            {"is_read": False},
            "alice@example.com",
        ),
    ],
)
async def test_list_inquiries_supports_common_filters(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
    params: dict[str, Any],
    expected_email: str,
) -> None:
    user = cast(
        User,
        admin_contact_records["reader_user"],
    )

    token = await login_user(
        client,
        email=user.email,
    )

    response = await client.get(
        ADMIN_CONTACT_URL,
        params=params,
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 1
    assert response.json()["items"][0]["email"] == expected_email


async def test_list_inquiries_supports_assignment_filters(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_contact_records["reader_user"],
    )
    assignee = cast(
        User,
        admin_contact_records["assigned_user"],
    )

    token = await login_user(
        client,
        email=reader.email,
    )

    assigned_only = await client.get(
        ADMIN_CONTACT_URL,
        params={
            "assigned_to_id": str(assignee.id),
        },
        headers=authorization_headers(
            token,
        ),
    )
    assigned_and_unassigned = await client.get(
        ADMIN_CONTACT_URL,
        params={
            "assigned_to_id": str(assignee.id),
            "include_unassigned": True,
        },
        headers=authorization_headers(
            token,
        ),
    )
    unassigned_only = await client.get(
        ADMIN_CONTACT_URL,
        params={
            "include_unassigned": True,
        },
        headers=authorization_headers(
            token,
        ),
    )

    assert assigned_only.status_code == 200, assigned_only.text
    assert assigned_only.json()["total_items"] == 2

    assert assigned_and_unassigned.status_code == 200
    assert assigned_and_unassigned.json()["total_items"] == 5

    assert unassigned_only.status_code == 200
    assert unassigned_only.json()["total_items"] == 3


async def test_list_inquiries_can_include_deleted_records(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_contact_records["reader_user"],
    )

    token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        ADMIN_CONTACT_URL,
        params={
            "include_deleted": True,
        },
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 6


async def test_statistics_returns_expected_counts(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_contact_records["reader_user"],
    )

    token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        f"{ADMIN_CONTACT_URL}/statistics",
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "new": 1,
        "in_progress": 1,
        "responded": 1,
        "closed": 1,
        "spam": 1,
        "unread": 1,
        "requires_attention": 2,
    }


async def test_assignee_options_use_contact_read_permission(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_contact_records["reader_user"],
    )

    assigned_user = cast(
        User,
        admin_contact_records["assigned_user"],
    )

    alternate_assignee = cast(
        User,
        admin_contact_records["alternate_assignee"],
    )

    inactive_assignee = cast(
        User,
        admin_contact_records["inactive_assignee"],
    )

    token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        f"{ADMIN_CONTACT_URL}/assignees",
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = response.json()

    option_ids = {item["id"] for item in payload}

    assert str(assigned_user.id) in option_ids
    assert str(alternate_assignee.id) in option_ids
    assert str(inactive_assignee.id) not in option_ids

    for option in payload:
        assert set(option) == {
            "id",
            "full_name",
            "email",
        }


async def test_project_options_use_contact_read_permission(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_contact_records["reader_user"],
    )

    published_project = cast(
        Project,
        admin_contact_records["published_project"],
    )

    draft_project = cast(
        Project,
        admin_contact_records["draft_project"],
    )

    token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        f"{ADMIN_CONTACT_URL}/projects",
        headers=authorization_headers(
            token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = response.json()

    option_ids = {item["id"] for item in payload}

    assert str(published_project.id) in option_ids
    assert str(draft_project.id) in option_ids

    for option in payload:
        assert set(option) == {
            "id",
            "title",
            "slug",
        }


async def test_inquiry_lookup_options_reject_missing_permission(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    outsider = cast(
        User,
        admin_contact_records["outsider_user"],
    )

    token = await login_user(
        client,
        email=outsider.email,
    )

    assignee_response = await client.get(
        f"{ADMIN_CONTACT_URL}/assignees",
        headers=authorization_headers(
            token,
        ),
    )

    project_response = await client.get(
        f"{ADMIN_CONTACT_URL}/projects",
        headers=authorization_headers(
            token,
        ),
    )

    assert assignee_response.status_code == 403
    assert assignee_response.json()["detail"]["code"] == ("insufficient_permissions")

    assert project_response.status_code == 403
    assert project_response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_get_deleted_inquiry_requires_include_deleted(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_contact_records["reader_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["deleted_inquiry"],
    )

    token = await login_user(
        client,
        email=reader.email,
    )

    hidden = await client.get(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}",
        headers=authorization_headers(
            token,
        ),
    )
    visible = await client.get(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}",
        params={
            "include_deleted": True,
        },
        headers=authorization_headers(
            token,
        ),
    )

    assert hidden.status_code == 404
    assert visible.status_code == 200, visible.text
    assert visible.json()["deleted_at"] is not None


async def test_update_inquiry_succeeds(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_contact_records["updater_user"],
    )
    assignee = cast(
        User,
        admin_contact_records["alternate_assignee"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["new_inquiry"],
    )

    token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}",
        headers=authorization_headers(
            token,
        ),
        json={
            "priority": "high",
            "assigned_to_id": str(assignee.id),
            "internal_notes": "  Follow up within one business day.  ",
            "inquiry_type": "contract",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["priority"] == "high"
    assert response.json()["assigned_to_id"] == str(assignee.id)
    assert response.json()["internal_notes"] == ("Follow up within one business day.")
    assert response.json()["inquiry_type"] == "contract"


@pytest.mark.parametrize(
    ("assignee_record", "status_code", "error_code"),
    [
        (
            None,
            404,
            "contact_inquiry_assignee_not_found",
        ),
        (
            "inactive_assignee",
            409,
            "contact_inquiry_assignee_inactive",
        ),
    ],
)
async def test_update_inquiry_rejects_invalid_assignee(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
    assignee_record: str | None,
    status_code: int,
    error_code: str,
) -> None:
    updater = cast(
        User,
        admin_contact_records["updater_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["new_inquiry"],
    )

    assignee_id = (
        uuid4()
        if assignee_record is None
        else cast(
            User,
            admin_contact_records[assignee_record],
        ).id
    )

    token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}",
        headers=authorization_headers(
            token,
        ),
        json={
            "assigned_to_id": str(assignee_id),
        },
    )

    assert response.status_code == status_code
    assert response.json()["detail"]["code"] == error_code


async def test_read_state_sets_and_clears_timestamp(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_contact_records["updater_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["new_inquiry"],
    )

    token = await login_user(
        client,
        email=updater.email,
    )

    mark_read = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}/read-state",
        headers=authorization_headers(
            token,
        ),
        json={
            "is_read": True,
        },
    )
    mark_unread = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}/read-state",
        headers=authorization_headers(
            token,
        ),
        json={
            "is_read": False,
        },
    )

    assert mark_read.status_code == 200, mark_read.text
    assert mark_read.json()["is_read"] is True
    assert mark_read.json()["read_at"] is not None

    assert mark_unread.status_code == 200, mark_unread.text
    assert mark_unread.json()["is_read"] is False
    assert mark_unread.json()["read_at"] is None


@pytest.mark.parametrize(
    ("record_name", "target_status"),
    [
        ("new_inquiry", "in_progress"),
        ("new_inquiry", "responded"),
        ("new_inquiry", "closed"),
        ("new_inquiry", "spam"),
        ("in_progress_inquiry", "new"),
        ("in_progress_inquiry", "responded"),
        ("in_progress_inquiry", "closed"),
        ("in_progress_inquiry", "spam"),
        ("responded_inquiry", "in_progress"),
        ("responded_inquiry", "closed"),
        ("responded_inquiry", "spam"),
        ("closed_inquiry", "in_progress"),
        ("closed_inquiry", "spam"),
        ("spam_inquiry", "new"),
        ("spam_inquiry", "in_progress"),
    ],
)
async def test_status_workflow_allows_supported_transitions(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
    record_name: str,
    target_status: str,
) -> None:
    updater = cast(
        User,
        admin_contact_records["updater_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records[record_name],
    )

    token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}/status",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": target_status,
            "reason": "Workflow transition integration test.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == target_status


async def test_status_workflow_rejects_invalid_transition(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_contact_records["updater_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["closed_inquiry"],
    )

    token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}/status",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": "new",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == (
        "contact_inquiry_invalid_status_transition"
    )


async def test_delete_and_restore_inquiry(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    manager = cast(
        User,
        admin_contact_records["manager_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["new_inquiry"],
    )

    token = await login_user(
        client,
        email=manager.email,
    )

    delete_response = await client.request(
        "DELETE",
        f"{ADMIN_CONTACT_URL}/{inquiry.id}",
        headers=authorization_headers(
            token,
        ),
        json={
            "reason": "Inquiry no longer required.",
        },
    )

    restore_response = await client.post(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}/restore",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": "in_progress",
            "priority": "high",
            "reason": "Inquiry requires renewed administrative review.",
        },
    )

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["deleted_at"] is not None

    assert restore_response.status_code == 200, restore_response.text
    assert restore_response.json()["deleted_at"] is None
    assert restore_response.json()["status"] == "in_progress"
    assert restore_response.json()["priority"] == "high"


async def test_restore_rejects_non_deleted_inquiry(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_contact_records["updater_user"],
    )
    inquiry = cast(
        ContactInquiry,
        admin_contact_records["new_inquiry"],
    )

    token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.post(
        f"{ADMIN_CONTACT_URL}/{inquiry.id}/restore",
        headers=authorization_headers(
            token,
        ),
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("contact_inquiry_conflict")


async def test_manager_can_complete_contact_lifecycle(
    client: AsyncClient,
    admin_contact_records: dict[str, object],
) -> None:
    manager = cast(
        User,
        admin_contact_records["manager_user"],
    )
    assignee = cast(
        User,
        admin_contact_records["assigned_user"],
    )

    public_response = await client.post(
        PUBLIC_CONTACT_URL,
        json=valid_public_payload(
            email="lifecycle@example.com",
            subject="Complete contact workflow",
            message=(
                "Please use this inquiry to verify the complete administrative "
                "contact workflow."
            ),
        ),
    )

    assert public_response.status_code == 201, public_response.text

    token = await login_user(
        client,
        email=manager.email,
    )

    list_response = await client.get(
        ADMIN_CONTACT_URL,
        params={
            "search": "lifecycle@example.com",
        },
        headers=authorization_headers(
            token,
        ),
    )

    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["total_items"] == 1

    inquiry_id = str(
        list_response.json()["items"][0]["id"],
    )

    update_response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry_id}",
        headers=authorization_headers(
            token,
        ),
        json={
            "priority": "urgent",
            "assigned_to_id": str(assignee.id),
            "internal_notes": "Manager lifecycle integration test.",
        },
    )
    progress_response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry_id}/status",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": "in_progress",
        },
    )
    responded_response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry_id}/status",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": "responded",
        },
    )
    closed_response = await client.patch(
        f"{ADMIN_CONTACT_URL}/{inquiry_id}/status",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": "closed",
        },
    )
    delete_response = await client.request(
        "DELETE",
        f"{ADMIN_CONTACT_URL}/{inquiry_id}",
        headers=authorization_headers(
            token,
        ),
        json={},
    )
    restore_response = await client.post(
        f"{ADMIN_CONTACT_URL}/{inquiry_id}/restore",
        headers=authorization_headers(
            token,
        ),
        json={
            "status": "new",
            "priority": "normal",
        },
    )

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["priority"] == "urgent"

    assert progress_response.status_code == 200
    assert progress_response.json()["status"] == "in_progress"

    assert responded_response.status_code == 200
    assert responded_response.json()["responded_at"] is not None

    assert closed_response.status_code == 200
    assert closed_response.json()["closed_at"] is not None

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_at"] is not None

    assert restore_response.status_code == 200
    assert restore_response.json()["deleted_at"] is None
    assert restore_response.json()["status"] == "new"
    assert restore_response.json()["priority"] == "normal"
    assert restore_response.json()["responded_at"] is None
    assert restore_response.json()["closed_at"] is None
