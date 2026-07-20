from app.db.model_registry import Base


EXPECTED_TABLES = {
    "email_verification_tokens",
    "login_attempts",
    "password_reset_tokens",
    "permissions",
    "refresh_tokens",
    "role_permissions",
    "roles",
    "sessions",
    "user_roles",
    "users",
}

ACCOUNT_TOKEN_COLUMNS = {
    "id",
    "user_id",
    "token_digest",
    "expires_at",
    "consumed_at",
    "revoked_at",
    "created_at",
    "updated_at",
    "deleted_at",
}


def test_all_identity_tables_are_registered() -> None:
    registered_tables = set(Base.metadata.tables.keys())

    assert EXPECTED_TABLES.issubset(registered_tables)


def test_users_table_uses_uuid_primary_key() -> None:
    users_table = Base.metadata.tables["users"]
    primary_key_columns = list(users_table.primary_key.columns)

    assert len(primary_key_columns) == 1
    assert primary_key_columns[0].name == "id"


def test_users_table_has_shared_audit_columns() -> None:
    users_table = Base.metadata.tables["users"]

    assert "created_at" in users_table.columns
    assert "updated_at" in users_table.columns
    assert "deleted_at" in users_table.columns


def test_email_verification_tokens_are_secure() -> None:
    table = Base.metadata.tables["email_verification_tokens"]

    assert ACCOUNT_TOKEN_COLUMNS.issubset(table.columns.keys())

    assert "token" not in table.columns
    assert "raw_token" not in table.columns
    assert "plain_token" not in table.columns

    assert table.c.token_digest.unique is True
    assert table.c.user_id.nullable is False
    assert table.c.expires_at.nullable is False


def test_password_reset_tokens_are_secure() -> None:
    table = Base.metadata.tables["password_reset_tokens"]

    assert ACCOUNT_TOKEN_COLUMNS.issubset(table.columns.keys())

    assert "token" not in table.columns
    assert "raw_token" not in table.columns
    assert "plain_token" not in table.columns

    assert table.c.token_digest.unique is True
    assert table.c.user_id.nullable is False
    assert table.c.expires_at.nullable is False
