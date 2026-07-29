"""add portfolio profile

Revision ID: a7e354695851
Revises: 291b9552d692
Create Date: 2026-07-28 23:56:41.735710

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision: str = "a7e354695851"
down_revision: Union[str, Sequence[str], None] = "291b9552d692"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


permission_table = table(
    "permissions",
    column("id", sa.Uuid()),
    column("code", sa.String()),
    column("name", sa.String()),
    column("description", sa.String()),
    column("is_active", sa.Boolean()),
)


PROFILE_PERMISSIONS = [
    (
        "profile.read",
        "Profile Read",
        "View portfolio profile.",
    ),
    (
        "profile.create",
        "Profile Create",
        "Create portfolio profile.",
    ),
    (
        "profile.update",
        "Profile Update",
        "Update portfolio profile.",
    ),
    (
        "profile.delete",
        "Profile Delete",
        "Delete or restore portfolio profile.",
    ),
]


def upgrade() -> None:
    """Create the portfolio profile table and profile permissions."""
    op.create_table(
        "profiles",
        sa.Column(
            "profile_key",
            sa.String(length=20),
            server_default=sa.text("'primary'"),
            nullable=False,
        ),
        sa.Column(
            "first_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "middle_name",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "last_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "display_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "professional_title",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "headline",
            sa.String(length=300),
            nullable=False,
        ),
        sa.Column(
            "short_bio",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "biography",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "location",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "country",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "primary_email",
            postgresql.CITEXT(),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(length=40),
            nullable=True,
        ),
        sa.Column(
            "website_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "resume_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "profile_image_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "years_of_experience",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "availability_status",
            sa.String(length=40),
            server_default=sa.text("'open_to_opportunities'"),
            nullable=False,
        ),
        sa.Column(
            "availability_message",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "is_public",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "seo_title",
            sa.String(length=70),
            nullable=True,
        ),
        sa.Column(
            "seo_description",
            sa.String(length=170),
            nullable=True,
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
            (
                "availability_status IN "
                "('available', 'open_to_opportunities', "
                "'limited_availability', 'unavailable')"
            ),
            name=op.f(
                "ck_profiles_profiles_availability_status_allowed",
            ),
        ),
        sa.CheckConstraint(
            "profile_key = 'primary'",
            name=op.f(
                "ck_profiles_profiles_profile_key_primary",
            ),
        ),
        sa.CheckConstraint(
            ("availability_message IS NULL OR length(btrim(availability_message)) > 0"),
            name=op.f(
                "ck_profiles_profiles_availability_message_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "country IS NULL OR length(btrim(country)) > 0",
            name=op.f(
                "ck_profiles_profiles_country_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(biography)) >= 50",
            name=op.f(
                "ck_profiles_profiles_biography_min_length",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(display_name)) >= 2",
            name=op.f(
                "ck_profiles_profiles_display_name_min_length",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(first_name)) >= 2",
            name=op.f(
                "ck_profiles_profiles_first_name_min_length",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(headline)) >= 5",
            name=op.f(
                "ck_profiles_profiles_headline_min_length",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(last_name)) >= 2",
            name=op.f(
                "ck_profiles_profiles_last_name_min_length",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(primary_email::text)) >= 3",
            name=op.f(
                "ck_profiles_profiles_primary_email_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(professional_title)) >= 2",
            name=op.f(
                "ck_profiles_profiles_professional_title_min_length",
            ),
        ),
        sa.CheckConstraint(
            "length(btrim(short_bio)) >= 20",
            name=op.f(
                "ck_profiles_profiles_short_bio_min_length",
            ),
        ),
        sa.CheckConstraint(
            "location IS NULL OR length(btrim(location)) > 0",
            name=op.f(
                "ck_profiles_profiles_location_not_blank",
            ),
        ),
        sa.CheckConstraint(
            ("middle_name IS NULL OR length(btrim(middle_name)) >= 2"),
            name=op.f(
                "ck_profiles_profiles_middle_name_min_length",
            ),
        ),
        sa.CheckConstraint(
            "phone IS NULL OR length(btrim(phone)) > 0",
            name=op.f(
                "ck_profiles_profiles_phone_not_blank",
            ),
        ),
        sa.CheckConstraint(
            ("profile_image_url IS NULL OR length(btrim(profile_image_url)) > 0"),
            name=op.f(
                "ck_profiles_profiles_profile_image_url_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "resume_url IS NULL OR length(btrim(resume_url)) > 0",
            name=op.f(
                "ck_profiles_profiles_resume_url_not_blank",
            ),
        ),
        sa.CheckConstraint(
            ("seo_description IS NULL OR length(btrim(seo_description)) > 0"),
            name=op.f(
                "ck_profiles_profiles_seo_description_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "seo_title IS NULL OR length(btrim(seo_title)) > 0",
            name=op.f(
                "ck_profiles_profiles_seo_title_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "timezone IS NULL OR length(btrim(timezone)) > 0",
            name=op.f(
                "ck_profiles_profiles_timezone_not_blank",
            ),
        ),
        sa.CheckConstraint(
            ("website_url IS NULL OR length(btrim(website_url)) > 0"),
            name=op.f(
                "ck_profiles_profiles_website_url_not_blank",
            ),
        ),
        sa.CheckConstraint(
            "years_of_experience >= 0",
            name=op.f(
                "ck_profiles_profiles_years_of_experience_non_negative",
            ),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f(
                "fk_profiles_created_by_id_users",
            ),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f(
                "fk_profiles_updated_by_id_users",
            ),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_profiles"),
        ),
        sa.UniqueConstraint(
            "profile_key",
            name=op.f("uq_profiles_profile_key"),
        ),
    )

    op.create_index(
        op.f("ix_profiles_availability_status"),
        "profiles",
        ["availability_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_profiles_created_by_id"),
        "profiles",
        ["created_by_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_profiles_deleted_at"),
        "profiles",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_profiles_is_public"),
        "profiles",
        ["is_public"],
        unique=False,
    )
    op.create_index(
        "ix_profiles_public",
        "profiles",
        ["is_public"],
        unique=False,
        postgresql_where=sa.text(
            "deleted_at IS NULL AND is_public = true",
        ),
    )
    op.create_index(
        op.f("ix_profiles_updated_by_id"),
        "profiles",
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
            for code, name, description in PROFILE_PERMISSIONS
        ],
    )


def downgrade() -> None:
    """Remove the portfolio profile table and profile permissions."""
    permission_codes = [code for code, _, _ in PROFILE_PERMISSIONS]

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
        op.f("ix_profiles_updated_by_id"),
        table_name="profiles",
    )
    op.drop_index(
        "ix_profiles_public",
        table_name="profiles",
        postgresql_where=sa.text(
            "deleted_at IS NULL AND is_public = true",
        ),
    )
    op.drop_index(
        op.f("ix_profiles_is_public"),
        table_name="profiles",
    )
    op.drop_index(
        op.f("ix_profiles_deleted_at"),
        table_name="profiles",
    )
    op.drop_index(
        op.f("ix_profiles_created_by_id"),
        table_name="profiles",
    )
    op.drop_index(
        op.f("ix_profiles_availability_status"),
        table_name="profiles",
    )
    op.drop_table("profiles")
