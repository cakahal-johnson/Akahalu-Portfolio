from enum import StrEnum

from app.schemas.portfolio.common import PaginatedResponse


class ContactInquiryType(StrEnum):
    GENERAL = "general"
    EMPLOYMENT = "employment"
    FREELANCE = "freelance"
    CONTRACT = "contract"
    COLLABORATION = "collaboration"
    PROJECT = "project"
    SUPPORT = "support"
    OTHER = "other"


class ContactInquiryStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESPONDED = "responded"
    CLOSED = "closed"
    SPAM = "spam"


class ContactInquiryPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


__all__ = [
    "ContactInquiryPriority",
    "ContactInquiryStatus",
    "ContactInquiryType",
    "PaginatedResponse",
]
