package com.akahalu.portfolio.data.portfolio.mapper

import com.akahalu.portfolio.data.portfolio.dto.ProjectCategoryDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectTechnologyDto
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnologyCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectVisibility
import kotlin.collections.emptyList
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class PortfolioMappersTest {

    @Test
    fun categoryDtoMapsToDomain() {
        val dto = ProjectCategoryDto(
            id = "category-1",
            name = "Web Development",
            slug = "web-development",
            description = "Web applications.",
            icon = "code",
            color = "#2563EB",
            sort_order = 1,
            seo_title = "Web Development Projects",
            seo_description = "Explore web projects.",
        )

        val result = dto.toDomain()

        assertEquals(
            "category-1",
            result.id,
        )
        assertEquals(
            "Web Development",
            result.name,
        )
        assertEquals(
            "web-development",
            result.slug,
        )
        assertEquals(
            1,
            result.sortOrder,
        )
        assertEquals(
            "Web Development Projects",
            result.seoTitle,
        )
    }

    @Test
    fun technologyCategoryMapsCorrectly() {
        val dto = ProjectTechnologyDto(
            id = "technology-1",
            name = "FastAPI",
            slug = "fastapi",
            category = "framework",
            icon = "fastapi",
            official_url = "https://fastapi.tiangolo.com",
            color = "#009688",
            sort_order = 1,
            description = "Python API framework.",
        )

        val result = dto.toDomain()

        assertEquals(
            ProjectTechnologyCategory.FRAMEWORK,
            result.category,
        )
        assertEquals(
            "FastAPI",
            result.name,
        )
    }

    @Test
    fun unknownTechnologyCategoryFallsBackToOther() {
        val dto = ProjectTechnologyDto(
            id = "technology-1",
            name = "Future Tool",
            slug = "future-tool",
            category = "future_category",
            sort_order = 0,
        )

        val result = dto.toDomain()

        assertEquals(
            ProjectTechnologyCategory.OTHER,
            result.category,
        )
    }

    @Test
    fun summaryProjectMapsWithDetailFieldsEmpty() {
        val dto = com.akahalu.portfolio.data.portfolio.dto.ProjectSummaryDto(
            id = "project-1",
            title = "Portfolio",
            slug = "portfolio",
            short_description = "Personal portfolio application.",
            status = "published",
            visibility = "public",
            is_featured = true,
            sort_order = 1,
        )

        val result = dto.toDomain()

        assertEquals(
            ProjectStatus.PUBLISHED,
            result.status,
        )
        assertEquals(
            ProjectVisibility.PUBLIC,
            result.visibility,
        )
        assertEquals(
            true,
            result.isFeatured,
        )
        assertNull(
            result.description,
        )
        assertEquals(
            emptyList(),
            result.media,
        )
    }

    @Test
    fun projectDtoMapsDetailedFields() {
        val dto = ProjectDto(
            id = "project-1",
            title = "Akahalu Portfolio",
            slug = "akahalu-portfolio",
            short_description = "Production-ready portfolio.",
            status = "published",
            visibility = "public",
            is_featured = true,
            sort_order = 1,
            description = "Full-stack personal portfolio.",
            repository_url = "https://github.com/example/project",
            live_url = "https://example.com",
        )

        val result = dto.toDomain()

        assertEquals(
            "Akahalu Portfolio",
            result.title,
        )
        assertEquals(
            "Full-stack personal portfolio.",
            result.description,
        )
        assertEquals(
            "https://github.com/example/project",
            result.repositoryUrl,
        )
        assertEquals(
            "https://example.com",
            result.liveUrl,
        )
    }
}