from app.db.model_registry import Base


EXPECTED_TABLES = {
    "permissions",
    "role_permissions",
    "roles",
    "user_roles",
    "users",
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
