from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
        ]
    )

    database_url: str = (
        "postgresql+psycopg://portfolio_user:"
        "portfolio_password@127.0.0.1:5432/portfolio_db"
    )

    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30

    redis_url: str = "redis://:portfolio_redis_password@127.0.0.1:6379/0"

    jwt_secret_key: str
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_issuer: str = "akahalu-portfolio-api"
    jwt_audience: str = "akahalu-portfolio-web"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    maximum_failed_login_attempts: int = 5
    account_lockout_minutes: int = 15

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "test"


@lru_cache
def get_settings() -> Settings:
    # jwt_secret_key is supplied through the environment by BaseSettings.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
