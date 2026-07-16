from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": ("fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"),
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=NAMING_CONVENTION,
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        nullable=False,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        self.deleted_at = None


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls: type[Any]) -> str:
        class_name = cls.__name__

        snake_case_name = "".join(
            (f"_{character.lower()}" if character.isupper() else character)
            for character in class_name
        ).lstrip("_")

        return f"{snake_case_name}s"


class BaseModel(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    TableNameMixin,
    Base,
):
    __abstract__ = True


class ReprMixin:
    def __repr__(self) -> str:
        mapper: Any = getattr(self, "__mapper__")
        primary_key_values: list[str] = []

        for primary_key in mapper.primary_key:
            value = getattr(self, primary_key.name)

            primary_key_values.append(f"{primary_key.name}={value!r}")

        joined_values = ", ".join(primary_key_values)

        return f"{self.__class__.__name__}({joined_values})"
