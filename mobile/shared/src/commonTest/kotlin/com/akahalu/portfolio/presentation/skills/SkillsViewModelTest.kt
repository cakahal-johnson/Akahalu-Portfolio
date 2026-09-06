@file:OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)

package com.akahalu.portfolio.presentation.skills

import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmission
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmissionResult
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnologyCategory
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

class SkillsViewModelTest {

    @Test
    fun initialStateIsLoading() = runTest {
        val repository = FakePortfolioRepository()

        val viewModel = SkillsViewModel(
            repository = repository,
            scope = CoroutineScope(
                UnconfinedTestDispatcher(testScheduler),
            ),
        )

        assertIs<SkillsUiState.Loading>(
            viewModel.uiState.value,
        )
    }

    @Test
    fun loadTechnologiesEmitsSuccess() = runTest {
        val technologies = listOf(
            ProjectTechnology(
                id = "technology-1",
                name = "FastAPI",
                slug = "fastapi",
                category = ProjectTechnologyCategory.FRAMEWORK,
                icon = "fastapi",
                officialUrl = "https://fastapi.tiangolo.com",
                color = "#009688",
                sortOrder = 1,
                description = "Python API framework.",
            ),
        )

        val repository = FakePortfolioRepository(
            technologies = technologies,
        )

        val viewModel = SkillsViewModel(
            repository = repository,
            scope = CoroutineScope(
                UnconfinedTestDispatcher(testScheduler),
            ),
        )

        viewModel.loadTechnologies()

        val state = assertIs<SkillsUiState.Success>(
            viewModel.uiState.value,
        )

        assertEquals(
            technologies,
            state.technologies,
        )
    }

    @Test
    fun loadTechnologiesSupportsMultipleTechnologies() = runTest {
        val technologies = listOf(
            ProjectTechnology(
                id = "technology-1",
                name = "Kotlin",
                slug = "kotlin",
                category = ProjectTechnologyCategory.LANGUAGE,
                icon = "kotlin",
                officialUrl = null,
                color = null,
                sortOrder = 1,
                description = null,
            ),
            ProjectTechnology(
                id = "technology-2",
                name = "Compose Multiplatform",
                slug = "compose-multiplatform",
                category = ProjectTechnologyCategory.FRAMEWORK,
                icon = "compose",
                officialUrl = null,
                color = null,
                sortOrder = 2,
                description = null,
            ),
        )

        val viewModel = SkillsViewModel(
            repository = FakePortfolioRepository(
                technologies = technologies,
            ),
            scope = CoroutineScope(
                UnconfinedTestDispatcher(testScheduler),
            ),
        )

        viewModel.loadTechnologies()

        val state = assertIs<SkillsUiState.Success>(
            viewModel.uiState.value,
        )

        assertEquals(
            2,
            state.technologies.size,
        )
        assertEquals(
            "Kotlin",
            state.technologies[0].name,
        )
        assertEquals(
            "Compose Multiplatform",
            state.technologies[1].name,
        )
    }

    @Test
    fun loadTechnologiesSupportsEmptyResponse() = runTest {
        val viewModel = SkillsViewModel(
            repository = FakePortfolioRepository(
                technologies = emptyList(),
            ),
            scope = CoroutineScope(
                UnconfinedTestDispatcher(testScheduler),
            ),
        )

        viewModel.loadTechnologies()

        val state = assertIs<SkillsUiState.Success>(
            viewModel.uiState.value,
        )

        assertEquals(
            emptyList(),
            state.technologies,
        )
    }

    @Test
    fun loadTechnologiesEmitsErrorWhenRepositoryFails() = runTest {
        val viewModel = SkillsViewModel(
            repository = FakePortfolioRepository(
                failure = IllegalStateException(
                    "Unable to reach portfolio API.",
                ),
            ),
            scope = CoroutineScope(
                UnconfinedTestDispatcher(testScheduler),
            ),
        )

        viewModel.loadTechnologies()

        val state = assertIs<SkillsUiState.Error>(
            viewModel.uiState.value,
        )

        assertEquals(
            "Unable to reach portfolio API.",
            state.message,
        )
    }

    private class FakePortfolioRepository(
        private val technologies: List<ProjectTechnology> = emptyList(),
        private val failure: Throwable? = null,
    ) : PortfolioRepository {

        override suspend fun getCategories(): List<ProjectCategory> {
            throw UnsupportedOperationException()
        }

        override suspend fun getCategory(
            slug: String,
        ): ProjectCategory {
            throw UnsupportedOperationException()
        }

        override suspend fun getTechnologies(
            category: String?,
        ): List<ProjectTechnology> {
            failure?.let { throw it }
            return technologies
        }

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
        ): List<Project> {
            throw UnsupportedOperationException()
        }

        override suspend fun getProject(
            slug: String,
        ): Project {
            throw UnsupportedOperationException()
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
            throw UnsupportedOperationException()
        }

        override suspend fun getFeaturedExperiences(
            limit: Int,
        ): List<Experience> {
            throw UnsupportedOperationException()
        }

        override suspend fun getExperience(
            slug: String,
        ): Experience {
            throw UnsupportedOperationException()
        }

        override suspend fun getProfile(): Profile {
            error("Not required for SkillsViewModelTest.")
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