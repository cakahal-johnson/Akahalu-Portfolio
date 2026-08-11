import pytest
from pydantic import ValidationError

from app.core.config import Settings


JWT_SECRET = "test-jwt-secret-key-with-sufficient-length"

CONTACT_SECRET = "test-contact-secret-key-with-sufficient-length"


def build_settings(
    **overrides: object,
) -> Settings:
    values: dict[
        str,
        object,
    ] = {
        "jwt_secret_key": JWT_SECRET,
        "contact_hash_secret_key": CONTACT_SECRET,
        "allowed_origins": [
            "https://portfolio.example.com",
        ],
        "trusted_hosts": [
            "portfolio.example.com",
            "backend",
        ],
    }

    values.update(overrides)

    return Settings.model_validate(values)


def test_production_disables_api_docs_by_default() -> None:
    settings = build_settings(
        environment="production",
    )

    assert settings.api_docs_are_enabled is False


def test_non_production_enables_api_docs_by_default() -> None:
    settings = build_settings(
        environment="local",
    )

    assert settings.api_docs_are_enabled is True


def test_api_docs_can_be_explicitly_enabled() -> None:
    settings = build_settings(
        environment="production",
        api_docs_enabled=True,
    )

    assert settings.api_docs_are_enabled is True


def test_production_rejects_debug_mode() -> None:
    with pytest.raises(
        ValidationError,
        match=("DEBUG must be false in production"),
    ):
        build_settings(
            environment="production",
            debug=True,
        )


def test_production_rejects_wildcard_cors_origin() -> None:
    with pytest.raises(
        ValidationError,
        match=("Wildcard CORS origins are not allowed"),
    ):
        build_settings(
            environment="production",
            allowed_origins=[
                "*",
            ],
        )


def test_production_rejects_localhost_origin() -> None:
    with pytest.raises(
        ValidationError,
        match=("Local development origins are not allowed"),
    ):
        build_settings(
            environment="production",
            allowed_origins=[
                "http://localhost:3000",
            ],
        )


def test_production_rejects_wildcard_trusted_host() -> None:
    with pytest.raises(
        ValidationError,
        match=("Wildcard trusted hosts are not allowed"),
    ):
        build_settings(
            environment="production",
            trusted_hosts=[
                "*",
            ],
        )
