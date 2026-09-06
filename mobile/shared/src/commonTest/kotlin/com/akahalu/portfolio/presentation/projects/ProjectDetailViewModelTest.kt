@file:OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)

package com.akahalu.portfolio.presentation.projects

import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmission
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmissionResult
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectLink
import com.akahalu.portfolio.domain.portfolio.model.ProjectMedia
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.model.ProjectVisibility
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceUntilIdle
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

class ProjectDetailViewModelTest {

    private val dispatcher = StandardTestDispatcher()

    @Test
    fun loadProject_emitsSuccess_whenRepositoryReturnsProject() {
        val expectedProject = createProject(slug = "akahalu-portfolio")
        val repository = FakePortfolioRepository(
            project = expectedProject,
        )
        val scope = TestScope(dispatcher)
        val viewModel = ProjectDetailViewModel(
            repository = repository,
            scope = scope,
        )

        viewModel.loadProject("akahalu-portfolio")
        scope.advanceUntilIdle()

        val state = viewModel.uiState.value

        assertIs<ProjectDetailUiState.Success>(state)
        assertEquals(expectedProject, state.project)
        assertEquals("akahalu-portfolio", repository.requestedSlug)
    }

    @Test
    fun loadProject_emitsError_whenRepositoryFails() {
        val repository = FakePortfolioRepository(
            failure = IllegalStateException("Project unavailable."),
        )
        val scope = TestScope(dispatcher)
        val viewModel = ProjectDetailViewModel(
            repository = repository,
            scope = scope,
        )

        viewModel.loadProject("missing-project")
        scope.advanceUntilIdle()

        val state = viewModel.uiState.value

        assertIs<ProjectDetailUiState.Error>(state)
        assertEquals("Project unavailable.", state.message)
    }

    @Test
    fun loadProject_emitsError_whenSlugIsBlank() {
        val repository = FakePortfolioRepository()
        val scope = TestScope(dispatcher)
        val viewModel = ProjectDetailViewModel(
            repository = repository,
            scope = scope,
        )

        viewModel.loadProject("   ")
        scope.advanceUntilIdle()

        val state = viewModel.uiState.value

        assertIs<ProjectDetailUiState.Error>(state)
        assertEquals(
            "Project slug must not be blank.",
            state.message,
        )
    }

    private fun createProject(slug: String): Project {
        return Project(
            id = "project-1",
            title = "Akahalu Portfolio",
            slug = slug,
            shortDescription = "Personal portfolio platform.",
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
            description = "A full-stack portfolio platform.",
            problemStatement = "Demonstrate professional software engineering work.",
            solutionSummary = "A modern Kotlin Multiplatform portfolio application.",
            keyFeatures = "Projects, experience, and contact information.",
            technicalHighlights = "Kotlin Multiplatform and Compose Multiplatform.",
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
        private val project: Project? = null,
        private val failure: Throwable? = null,
    ) : PortfolioRepository {

        var requestedSlug: String? = null
            private set

        override suspend fun getCategories(): List<ProjectCategory> =
            emptyList()

        override suspend fun getCategory(
            slug: String,
        ): ProjectCategory {
            throw UnsupportedOperationException()
        }

        override suspend fun getTechnologies(
            category: String?,
        ): List<ProjectTechnology> = emptyList()

        override suspend fun getTechnology(
            slug: String,
        ): ProjectTechnology {
            throw UnsupportedOperationException()
        }

        override suspend fun getProjects(
            page: Int,
            pageSize: Int,
            search: String?,
            categorySlug: String?,
            technologySlug: String?,
            isFeatured: Boolean?,
        ): ProjectPage {
            throw UnsupportedOperationException()
        }

        override suspend fun getFeaturedProjects(
            limit: Int,
        ): List<Project> = emptyList()

        override suspend fun getProject(
            slug: String,
        ): Project {
            requestedSlug = slug

            failure?.let { throw it }

            return project ?: throw IllegalStateException(
                "No project configured.",
            )
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
            error("Not required for ProjectDetailViewModelTest.")
        }

        override suspend fun submitContactInquiry(
            submission: ContactInquirySubmission,
        ): ContactInquirySubmissionResult {
            throw UnsupportedOperationException(
                "submitContactInquiry is not used by this test.",
            )
        }
    }
}