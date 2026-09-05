package com.akahalu.portfolio.data.portfolio.mapper

import com.akahalu.portfolio.data.portfolio.dto.ProfileDto
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class ProfileMappersTest {

    @Test
    fun mapsCompleteProfileToDomain() {
        val dto = ProfileDto(
            first_name = "Akahalu",
            middle_name = "Chinonso",
            last_name = "Vitalis",
            display_name = "Akahalu Vitalis",
            professional_title = "Full-Stack Software Developer",
            headline = "Building secure and scalable applications.",
            short_bio = "Software developer focused on modern applications.",
            biography = "A professional software developer building secure applications.",
            location = "Regina, Saskatchewan",
            country = "Canada",
            timezone = "America/Regina",
            primary_email = "contact@example.com",
            phone = "+1 306 555 0100",
            website_url = "https://example.com",
            resume_url = "https://example.com/resume.pdf",
            profile_image_url = "https://example.com/profile.jpg",
            years_of_experience = 6,
            availability_status = "open_to_opportunities",
            availability_message = "Open to software development opportunities.",
            is_public = true,
            seo_title = "Akahalu Vitalis",
            seo_description = "Full-stack software developer.",
        )

        val profile = dto.toDomain()

        assertEquals("Akahalu", profile.firstName)
        assertEquals("Chinonso", profile.middleName)
        assertEquals("Vitalis", profile.lastName)
        assertEquals("Akahalu Vitalis", profile.displayName)
        assertEquals(
            "Full-Stack Software Developer",
            profile.professionalTitle,
        )
        assertEquals(
            ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES,
            profile.availabilityStatus,
        )
        assertEquals("Regina, Saskatchewan", profile.location)
        assertEquals("Canada", profile.country)
        assertEquals("contact@example.com", profile.primaryEmail)
        assertEquals(6, profile.yearsOfExperience)
        assertEquals(true, profile.isPublic)
    }

    @Test
    fun mapsNullableProfileFields() {
        val dto = ProfileDto(
            first_name = "Akahalu",
            last_name = "Vitalis",
            display_name = "Akahalu Vitalis",
            professional_title = "Software Developer",
            headline = "Building modern applications.",
            short_bio = "Software developer focused on modern applications.",
            biography = "A professional software developer.",
            primary_email = "contact@example.com",
        )

        val profile = dto.toDomain()

        assertNull(profile.middleName)
        assertNull(profile.location)
        assertNull(profile.country)
        assertNull(profile.timezone)
        assertNull(profile.phone)
        assertNull(profile.websiteUrl)
        assertNull(profile.resumeUrl)
        assertNull(profile.profileImageUrl)
        assertNull(profile.availabilityMessage)
    }

    @Test
    fun mapsAllKnownAvailabilityStatuses() {
        val statuses = mapOf(
            "available" to ProfileAvailabilityStatus.AVAILABLE,
            "open_to_opportunities" to
                    ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES,
            "limited_availability" to
                    ProfileAvailabilityStatus.LIMITED_AVAILABILITY,
            "unavailable" to ProfileAvailabilityStatus.UNAVAILABLE,
        )

        statuses.forEach { (rawValue, expected) ->
            val dto = createMinimalProfileDto(
                availabilityStatus = rawValue,
            )

            assertEquals(
                expected,
                dto.toDomain().availabilityStatus,
            )
        }
    }

    @Test
    fun unknownAvailabilityStatusDefaultsToUnavailable() {
        val dto = createMinimalProfileDto(
            availabilityStatus = "unexpected_status",
        )

        assertEquals(
            ProfileAvailabilityStatus.UNAVAILABLE,
            dto.toDomain().availabilityStatus,
        )
    }

    private fun createMinimalProfileDto(
        availabilityStatus: String,
    ): ProfileDto {
        return ProfileDto(
            first_name = "Akahalu",
            last_name = "Vitalis",
            display_name = "Akahalu Vitalis",
            professional_title = "Software Developer",
            headline = "Building modern applications.",
            short_bio = "Software developer focused on modern applications.",
            biography = "A professional software developer.",
            primary_email = "contact@example.com",
            availability_status = availabilityStatus,
        )
    }
}
