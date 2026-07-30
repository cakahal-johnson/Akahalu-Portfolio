"""Add portfolio experiences.

Revision ID: 17f167659ec9
Revises: a7e354695851
Create Date: 2026-07-29 13:11:20.683870
"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table


# Revision identifiers used by Alembic.
revision: str = "17f167659ec9"
down_revision: str | Sequence[str] | None = "a7e354695851"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


permission_table = table(
    "permissions",
    column(
        "id",
        sa.Uuid(),
    ),
    column(
        "code",
        sa.String(),
    ),
    column(
        "name",
        sa.String(),
    ),
    column(
        "description",
        sa.String(),
    ),
    column(
        "is_active",
        sa.Boolean(),
    ),
)


EXPERIENCE_PERMISSIONS = [
    (
        "experience.read",
        "Experience Read",
        "View portfolio experiences.",
    ),
    (
        "experience.create",
        "Experience Create",
        "Create portfolio experiences.",
    ),
    (
        "experience.update",
        "Experience Update",
        "Update portfolio experiences.",
    ),
    (
        "experience.delete",
        "Experience Delete",
        "Delete or restore portfolio experiences.",
    ),
]


def upgrade() -> None:
    """Create the portfolio experiences table and permissions."""

    op.create_table(
        "experiences",
        sa.Column(
            "company_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "job_title",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "slug",
            postgresql.CITEXT(),
            nullable=False,
        ),
        sa.Column(
            "employment_type",
            sa.String(length=30),
            server_default=sa.text("'full_time'"),
            nullable=False,
        ),
        sa.Column(
            "location",
            sa.String(length=250),
            nullable=True,
        ),
        sa.Column(
            "location_type",
            sa.String(length=20),
            server_default=sa.text("'onsite'"),
            nullable=False,
        ),
        sa.Column(
            "start_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "is_current",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "summary",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "responsibilities",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "achievements",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "company_website",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "company_logo_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "is_featured",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_public",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "created_by_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "updated_by_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            """
            employment_type IN (
                'full_time',
                'part_time',
                'contract',
                'freelance',
                'internship',
                'apprenticeship',
                'temporary',
                'volunteer',
                'self_employed',
                'other'
            )
            """,
            name=op.f("ck_experiences_experiences_employment_type_allowed"),
        ),
        sa.CheckConstraint(
            """
            location_type IN (
                'onsite',
                'remote',
                'hybrid'
            )
            """,
            name=op.f("ck_experiences_experiences_location_type_allowed"),
        ),
        sa.CheckConstraint(
            """
            achievements IS NULL
            OR length(btrim(achievements)) > 0
            """,
            name=op.f("ck_experiences_experiences_achievements_not_blank"),
        ),
        sa.CheckConstraint(
            """
            company_logo_url IS NULL
            OR length(btrim(company_logo_url)) > 0
            """,
            name=op.f("ck_experiences_experiences_company_logo_url_not_blank"),
        ),
        sa.CheckConstraint(
            """
            company_website IS NULL
            OR length(btrim(company_website)) > 0
            """,
            name=op.f("ck_experiences_experiences_company_website_not_blank"),
        ),
        sa.CheckConstraint(
            """
            end_date IS NULL
            OR end_date >= start_date
            """,
            name=op.f("ck_experiences_experiences_end_date_not_before_start"),
        ),
        sa.CheckConstraint(
            """
            is_current = false
            OR end_date IS NULL
            """,
            name=op.f("ck_experiences_experiences_current_has_no_end_date"),
        ),
        sa.CheckConstraint(
            """
            is_featured = false
            OR is_public = true
            """,
            name=op.f("ck_experiences_experiences_featured_requires_public"),
        ),
        sa.CheckConstraint(
            """
            responsibilities IS NULL
            OR length(btrim(responsibilities)) > 0
            """,
            name=op.f("ck_experiences_experiences_responsibilities_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(company_name)) >= 2",
            name=op.f("ck_experiences_experiences_company_name_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(job_title)) >= 2",
            name=op.f("ck_experiences_experiences_job_title_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(slug::text)) >= 2",
            name=op.f("ck_experiences_experiences_slug_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(summary)) >= 10",
            name=op.f("ck_experiences_experiences_summary_min_length"),
        ),
        sa.CheckConstraint(
            """
            location IS NULL
            OR length(btrim(location)) > 0
            """,
            name=op.f("ck_experiences_experiences_location_not_blank"),
        ),
        sa.CheckConstraint(
            "sort_order >= 0",
            name=op.f("ck_experiences_experiences_sort_order_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_experiences_created_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_experiences_updated_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_experiences"),
        ),
    )

    op.create_index(
        "ix_experiences_admin_listing",
        "experiences",
        [
            "is_public",
            "is_featured",
            "is_current",
            "sort_order",
            "start_date",
        ],
        unique=False,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_index(
        op.f("ix_experiences_created_by_id"),
        "experiences",
        ["created_by_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_deleted_at"),
        "experiences",
        ["deleted_at"],
        unique=False,
    )

    op.create_index(
        "ix_experiences_employment_filter",
        "experiences",
        [
            "employment_type",
            "location_type",
            "start_date",
        ],
        unique=False,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_index(
        op.f("ix_experiences_employment_type"),
        "experiences",
        ["employment_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_end_date"),
        "experiences",
        ["end_date"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_is_current"),
        "experiences",
        ["is_current"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_is_featured"),
        "experiences",
        ["is_featured"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_is_public"),
        "experiences",
        ["is_public"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_location_type"),
        "experiences",
        ["location_type"],
        unique=False,
    )

    op.create_index(
        "ix_experiences_public_listing",
        "experiences",
        [
            "is_current",
            "is_featured",
            "sort_order",
            "start_date",
        ],
        unique=False,
        postgresql_where=sa.text("deleted_at IS NULL AND is_public = true"),
    )

    op.create_index(
        op.f("ix_experiences_slug"),
        "experiences",
        ["slug"],
        unique=True,
    )

    op.create_index(
        op.f("ix_experiences_start_date"),
        "experiences",
        ["start_date"],
        unique=False,
    )

    op.create_index(
        op.f("ix_experiences_updated_by_id"),
        "experiences",
        ["updated_by_id"],
        unique=False,
    )

    op.bulk_insert(
        permission_table,
        [
            {
                "id": uuid4(),
                "code": code,
                "name": name,
                "description": description,
                "is_active": True,
            }
            for code, name, description in EXPERIENCE_PERMISSIONS
        ],
    )


def downgrade() -> None:
    """Remove the portfolio experiences table and permissions."""

    permission_codes = [code for code, _, _ in EXPERIENCE_PERMISSIONS]

    role_permissions_table = table(
        "role_permissions",
        column(
            "permission_id",
            sa.Uuid(),
        ),
    )

    permission_ids = sa.select(
        permission_table.c.id,
    ).where(
        permission_table.c.code.in_(
            permission_codes,
        ),
    )

    op.execute(
        role_permissions_table.delete().where(
            role_permissions_table.c.permission_id.in_(
                permission_ids,
            ),
        ),
    )

    op.execute(
        permission_table.delete().where(
            permission_table.c.code.in_(
                permission_codes,
            ),
        ),
    )

    op.drop_index(
        op.f("ix_experiences_updated_by_id"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_start_date"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_slug"),
        table_name="experiences",
    )

    op.drop_index(
        "ix_experiences_public_listing",
        table_name="experiences",
        postgresql_where=sa.text("deleted_at IS NULL AND is_public = true"),
    )

    op.drop_index(
        op.f("ix_experiences_location_type"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_is_public"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_is_featured"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_is_current"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_end_date"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_employment_type"),
        table_name="experiences",
    )

    op.drop_index(
        "ix_experiences_employment_filter",
        table_name="experiences",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.drop_index(
        op.f("ix_experiences_deleted_at"),
        table_name="experiences",
    )

    op.drop_index(
        op.f("ix_experiences_created_by_id"),
        table_name="experiences",
    )

    op.drop_index(
        "ix_experiences_admin_listing",
        table_name="experiences",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.drop_table("experiences")
