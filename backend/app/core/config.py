from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Akahalu Portfolio API"
    app_version: str = "0.1.0"

    environment: Literal[
        "local",
        "test",
        "staging",
        "production",
    ] = "local"

    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    api_docs_enabled: bool | None = None

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
        ]
    )

    trusted_hosts: list[str] = Field(
        default_factory=lambda: [
            "localhost",
            "127.0.0.1",
            "testserver",
            "backend",
        ]
    )

    database_url: str = (
        "postgresql+psycopg://portfolio_user:"
        "portfolio_password@127.0.0.1:5432/portfolio_db"
    )

    test_database_url: str | None = None

    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30

    redis_url: str = "redis://:portfolio_redis_password@127.0.0.1:6379/0"

    jwt_secret_key: str

    jwt_algorithm: Literal["HS256"] = "HS256"

    jwt_issuer: str = "akahalu-portfolio-api"
    jwt_audience: str = "akahalu-portfolio-web"

    contact_hash_secret_key: str

    contact_duplicate_window_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
    )

    contact_user_agent_max_length: int = Field(
        default=500,
        ge=100,
        le=512,
    )

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    email_verification_expire_hours: int = 24
    password_reset_expire_minutes: int = 60

    maximum_failed_login_attempts: int = 5
    account_lockout_minutes: int = 15

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "test"

    @property
    def api_docs_are_enabled(self) -> bool:
        if self.api_docs_enabled is not None:
            return self.api_docs_enabled

        return not self.is_production

    @model_validator(mode="after")
    def validate_production_settings(
        self,
    ) -> Self:
        if not self.is_production:
            return self

        if self.debug:
            raise ValueError("DEBUG must be false in production.")

        if not self.allowed_origins:
            raise ValueError(
                "ALLOWED_ORIGINS must contain at least one production origin."
            )

        normalized_origins = {origin.strip().lower() for origin in self.allowed_origins}

        if "*" in normalized_origins:
            raise ValueError("Wildcard CORS origins are not allowed in production.")

        insecure_origins = [
            origin
            for origin in normalized_origins
            if (
                origin.startswith("http://localhost")
                or origin.startswith("http://127.0.0.1")
            )
        ]

        if insecure_origins:
            raise ValueError("Local development origins are not allowed in production.")

        if not self.trusted_hosts:
            raise ValueError("TRUSTED_HOSTS must contain at least one production host.")

        normalized_hosts = {host.strip().lower() for host in self.trusted_hosts}

        if "*" in normalized_hosts:
            raise ValueError("Wildcard trusted hosts are not allowed in production.")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
