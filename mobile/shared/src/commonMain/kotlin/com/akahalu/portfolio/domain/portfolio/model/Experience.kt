package com.akahalu.portfolio.domain.portfolio.model

enum class EmploymentType {
    FULL_TIME,
    PART_TIME,
    CONTRACT,
    FREELANCE,
    INTERNSHIP,
    APPRENTICESHIP,
    TEMPORARY,
    VOLUNTEER,
    SELF_EMPLOYED,
    OTHER,
}

enum class ExperienceLocationType {
    ONSITE,
    REMOTE,
    HYBRID,
}

data class Experience(
    val id: String,
    val companyName: String,
    val jobTitle: String,
    val slug: String,
    val employmentType: EmploymentType,
    val location: String?,
    val locationType: ExperienceLocationType,
    val startDate: String,
    val endDate: String?,
    val isCurrent: Boolean,
    val summary: String,
    val companyWebsite: String?,
    val companyLogoUrl: String?,
    val sortOrder: Int,
    val isFeatured: Boolean,
    val responsibilities: String?,
    val achievements: String?,
)

data class ExperiencePage(
    val items: List<Experience>,
    val page: Int,
    val pageSize: Int,
    val totalItems: Int,
    val totalPages: Int,
    val hasNextPage: Boolean,
    val hasPreviousPage: Boolean,
)