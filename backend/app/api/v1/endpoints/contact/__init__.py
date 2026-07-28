from app.api.v1.endpoints.contact.admin import (
    router as admin_contact_inquiries_router,
)
from app.api.v1.endpoints.contact.public import (
    router as public_contact_inquiries_router,
)


__all__ = [
    "admin_contact_inquiries_router",
    "public_contact_inquiries_router",
]
