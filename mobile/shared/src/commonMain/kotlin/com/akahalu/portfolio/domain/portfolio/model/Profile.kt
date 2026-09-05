package com.akahalu.portfolio.domain.portfolio.model

enum class ProfileAvailabilityStatus {
    AVAILABLE,
    OPEN_TO_OPPORTUNITIES,
    LIMITED_AVAILABILITY,
    UNAVAILABLE,
}

data class Profile(
    val firstName: String,
    val middleName: String?,
    val lastName: String,
    val displayName: String,
    val professionalTitle: String,
    val headline: String,
    val shortBio: String,
    val biography: String,
    val location: String?,
    val country: String?,
    val timezone: String?,
    val primaryEmail: String,
    val phone: String?,
    val websiteUrl: String?,
    val resumeUrl: String?,
    val profileImageUrl: String?,
    val yearsOfExperience: Int,
    val availabilityStatus: ProfileAvailabilityStatus,
    val availabilityMessage: String?,
    val isPublic: Boolean,
    val seoTitle: String?,
    val seoDescription: String?,
)
