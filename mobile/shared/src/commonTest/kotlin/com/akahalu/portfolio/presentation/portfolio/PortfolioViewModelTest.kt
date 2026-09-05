@file:OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
package com.akahalu.portfolio.presentation.portfolio

import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.domain.portfolio.model.ProjectVisibility
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

class PortfolioViewModelTest {

    @Test
    fun loadPortfolioEmitsSuccess() = runTest {
        val project = createProject(
            slug = "portfolio",
        )

        val repository = FakePortfolioRepository(
            featuredProjects = listOf(project),
            projectPage = ProjectPage(
                items = listOf(project),
                page = 1,
                pageSize = 20,
                totalItems = 1,
                totalPages = 1,
                hasNextPage = false,
                hasPreviousPage = false,
            ),
        )

        val viewModel = PortfolioViewModel(
            repository = repository,
            scope = this,
        )

        viewModel.loadPortfolio()

        advanceUntilIdle()

        val state = viewModel.uiState.value

        assertIs<PortfolioUiState.Success>(state)

        assertEquals(
            listOf(project),
            state.featuredProjects,
        )

        assertEquals(
            listOf(project),
            state.projectPage.items,
        )
    }

    @Test
    fun loadPortfolioEmitsErrorWhenRepositoryFails() = runTest {
        val repository = FakePortfolioRepository(
            error = IllegalStateException(
                "Portfolio unavailable",
            ),
        )

        val viewModel = PortfolioViewModel(
            repository = repository,
            scope = this,
        )

        viewModel.loadPortfolio()

        advanceUntilIdle()

        val state = viewModel.uiState.value

        assertIs<PortfolioUiState.Error>(state)

        assertEquals(
            "Portfolio unavailable",
            state.message,
        )
    }

    private fun createProject(
        slug: String,
    ): Project {
        return Project(
            id = "project-1",
            title = "Test Project",
            slug = slug,
            shortDescription = "Test project description",
            status = ProjectStatus.PUBLISHED,
            visibility = ProjectVisibility.PUBLIC,
            isFeatured = true,
            sortOrder = 1,
            thumbnailUrl = null,
            startedAt = null,
            completedAt = null,
            publishedAt = null,
            category = null,
            technologies = emptyList(),
            description = "Detailed project description",
            problemStatement = null,
            solutionSummary = null,
            keyFeatures = null,
            technicalHighlights = null,
            repositoryUrl = null,
            liveUrl = null,
            caseStudyUrl = null,
            seoTitle = null,
            seoDescription = null,
            media = emptyList(),
            links = emptyList(),
        )
    }

    private class FakePortfolioRepository(
        private val featuredProjects: List<Project> = emptyList(),
        private val projectPage: ProjectPage = ProjectPage(
            items = emptyList(),
            page = 1,
            pageSize = 20,
            totalItems = 0,
            totalPages = 0,
            hasNextPage = false,
            hasPreviousPage = false,
        ),
        private val error: Throwable? = null,
    ) : PortfolioRepository {

        override suspend fun getCategories(): List<com.akahalu.portfolio.domain.portfolio.model.ProjectCategory> {
            error?.let { throw it }
            return emptyList()
        }

        override suspend fun getCategory(
            slug: String,
        ): com.akahalu.portfolio.domain.portfolio.model.ProjectCategory {
            error?.let { throw it }

            throw UnsupportedOperationException(
                "getCategory is not used by this test.",
            )
        }

        override suspend fun getTechnologies(
            category: String?,
        ): List<com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology> {
            error?.let { throw it }
            return emptyList()
        }

        override suspend fun getTechnology(
            slug: String,
        ): com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology {
            error?.let { throw it }

            throw UnsupportedOperationException(
                "getTechnology is not used by this test.",
            )
        }

        override suspend fun getProjects(
            page: Int,
            pageSize: Int,
            search: String?,
            categorySlug: String?,
            technologySlug: String?,
            isFeatured: Boolean?,
        ): ProjectPage {
            error?.let { throw it }

            return projectPage
        }

        override suspend fun getFeaturedProjects(
            limit: Int,
        ): List<Project> {
            error?.let { throw it }

            return featuredProjects
        }

        override suspend fun getProject(
            slug: String,
        ): Project {
            error?.let { throw it }

            return projectPage.items.first {
                it.slug == slug
            }
        }

        override suspend fun getExperiences(
            page: Int,
            pageSize: Int,
            search: String?,
            employmentType: String?,
            locationType: String?,
            isCurrent: Boolean?,
            isFeatured: Boolean?,
        ): ExperiencePage {
            return ExperiencePage(
                items = emptyList(),
                page = page,
                pageSize = pageSize,
                totalItems = 0,
                totalPages = 0,
                hasNextPage = false,
                hasPreviousPage = false,
            )
        }

        override suspend fun getFeaturedExperiences(
            limit: Int,
        ): List<Experience> {
            return emptyList()
        }

        override suspend fun getExperience(
            slug: String,
        ): Experience {
            error("Experience is not used by this test.")
        }

        override suspend fun getProfile(): Profile {
            error("Not required for PortfolioViewModelTest.")
        }
    }
}
