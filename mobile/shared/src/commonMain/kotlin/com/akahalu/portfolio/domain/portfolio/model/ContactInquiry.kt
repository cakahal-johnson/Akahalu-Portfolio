package com.akahalu.portfolio.domain.portfolio.model

enum class ContactInquiryType(
    val apiValue: String,
    val displayName: String,
) {
    GENERAL(
        apiValue = "general",
        displayName = "General",
    ),
    EMPLOYMENT(
        apiValue = "employment",
        displayName = "Employment",
    ),
    FREELANCE(
        apiValue = "freelance",
        displayName = "Freelance",
    ),
    CONTRACT(
        apiValue = "contract",
        displayName = "Contract",
    ),
    COLLABORATION(
        apiValue = "collaboration",
        displayName = "Collaboration",
    ),
    PROJECT(
        apiValue = "project",
        displayName = "Project",
    ),
    SUPPORT(
        apiValue = "support",
        displayName = "Support",
    ),
    OTHER(
        apiValue = "other",
        displayName = "Other",
    ),
}

data class ContactInquirySubmission(
    val name: String,
    val email: String,
    val phone: String? = null,
    val company: String? = null,
    val subject: String,
    val message: String,
    val inquiryType: ContactInquiryType = ContactInquiryType.GENERAL,
    val projectId: String? = null,
    val consentGiven: Boolean = false,
    val sourcePage: String? = "mobile/contact",
)

data class ContactInquirySubmissionResult(
    val message: String,
)