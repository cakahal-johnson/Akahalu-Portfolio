from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class DatabaseSchema(SchemaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
