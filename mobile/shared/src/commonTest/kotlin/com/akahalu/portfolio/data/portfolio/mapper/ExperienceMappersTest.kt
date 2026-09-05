package com.akahalu.portfolio.data.portfolio.mapper

import com.akahalu.portfolio.data.portfolio.dto.ExperienceSummaryDto
import com.akahalu.portfolio.domain.portfolio.model.EmploymentType
import com.akahalu.portfolio.domain.portfolio.model.ExperienceLocationType
import kotlin.test.Test
import kotlin.test.assertEquals

class ExperienceMappersTest {

    @Test
    fun summaryDto_mapsToDomain() {
        val dto = ExperienceSummaryDto(
            id = "experience-1",
            company_name = "Tech Company",
            job_title = "Software Developer",
            slug = "software-developer",
            employment_type = "full_time",
            location = "Regina, Canada",
            location_type = "hybrid",
            start_date = "2024-01-01",
            end_date = null,
            is_current = true,
            summary = "Built production software.",
            company_website = "https://example.com",
            company_logo_url = null,
            sort_order = 1,
            is_featured = true,
        )

        val result = dto.toDomain()

        assertEquals("experience-1", result.id)
        assertEquals(
            "Tech Company",
            result.companyName,
        )
        assertEquals(
            "Software Developer",
            result.jobTitle,
        )
        assertEquals(
            EmploymentType.FULL_TIME,
            result.employmentType,
        )
        assertEquals(
            ExperienceLocationType.HYBRID,
            result.locationType,
        )
        assertEquals(true, result.isCurrent)
        assertEquals(true, result.isFeatured)
    }

    @Test
    fun unknownEnumValues_fallBackSafely() {
        val dto = ExperienceSummaryDto(
            id = "experience-2",
            company_name = "Company",
            job_title = "Developer",
            slug = "developer",
            employment_type = "future_type",
            location_type = "future_location",
            start_date = "2025-01-01",
            summary = "A valid summary.",
            is_current = false,
            is_featured = false,
            sort_order = 0,
        )

        val result = dto.toDomain()

        assertEquals(
            EmploymentType.OTHER,
            result.employmentType,
        )

        assertEquals(
            ExperienceLocationType.ONSITE,
            result.locationType,
        )
    }
}