from typing import Annotated
from uuid import UUID

from sqlalchemy.orm import mapped_column


UUIDPrimaryKey = Annotated[
    UUID,
    mapped_column(
        primary_key=True,
        nullable=False,
    ),
]
