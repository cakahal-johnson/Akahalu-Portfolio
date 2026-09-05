package com.akahalu.portfolio.presentation.experience

import com.akahalu.portfolio.domain.portfolio.model.EmploymentType
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperienceLocationType
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

@OptIn(ExperimentalCoroutinesApi::class)
class ExperienceViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    private lateinit var repository: FakePortfolioRepository
    private lateinit var viewModel: ExperienceViewModel

    @BeforeTest
    fun setUp() {
        Dispatchers.setMain(testDispatcher)

        repository = FakePortfolioRepository()

        viewModel = ExperienceViewModel(
            repository = repository,
            scope = CoroutineScope(testDispatcher),
        )
    }

    @AfterTest
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun loadExperiences_success_updatesStateWithExperiences() =
        runTest {
            repository.experiencePage = ExperiencePage(
                items = listOf(
                    sampleExperience(
                        slug = "software-developer",
                    ),
                ),
                page = 1,
                pageSize = 20,
                totalItems = 1,
                totalPages = 1,
                hasNextPage = false,
                hasPreviousPage = false,
            )

            viewModel.loadExperiences()

            testDispatcher.scheduler.advanceUntilIdle()

            val state = assertIs<ExperienceUiState.Success>(
                viewModel.uiState.value,
            )

            assertEquals(
                1,
                state.experiences.size,
            )
            assertEquals(
                "software-developer",
                state.experiences.first().slug,
            )
            assertEquals(
                "Akahalu Technologies",
                state.experiences.first().companyName,
            )
            assertEquals(
                "Software Developer",
                state.experiences.first().jobTitle,
            )
        }

    @Test
    fun loadExperiences_success_mapsMultipleExperiences() =
        runTest {
            repository.experiencePage = ExperiencePage(
                items = listOf(
                    sampleExperience(
                        slug = "software-developer",
                    ),
                    sampleExperience(
                        slug = "technology-tutor",
                    ),
                ),
                page = 1,
                pageSize = 20,
                totalItems = 2,
                totalPages = 1,
                hasNextPage = false,
                hasPreviousPage = false,
            )

            viewModel.loadExperiences()

            testDispatcher.scheduler.advanceUntilIdle()

            val state = assertIs<ExperienceUiState.Success>(
                viewModel.uiState.value,
            )

            assertEquals(
                2,
                state.experiences.size,
            )
            assertEquals(
                "software-developer",
                state.experiences[0].slug,
            )
            assertEquals(
                "technology-tutor",
                state.experiences[1].slug,
            )
        }

    @Test
    fun loadExperiences_failure_updatesStateToError() =
        runTest {
            repository.error = IllegalStateException(
                "Unable to load experiences.",
            )

            viewModel.loadExperiences()

            testDispatcher.scheduler.advanceUntilIdle()

            val state = assertIs<ExperienceUiState.Error>(
                viewModel.uiState.value,
            )

            assertEquals(
                "Unable to load experiences.",
                state.message,
            )
        }

    @Test
    fun initialState_isLoading() {
        assertIs<ExperienceUiState.Loading>(
            viewModel.uiState.value,
        )
    }

    private fun sampleExperience(
        slug: String,
    ): Experience {
        return Experience(
            id = "experience-$slug",
            companyName = "Akahalu Technologies",
            jobTitle = "Software Developer",
            slug = slug,
            employmentType = EmploymentType.FULL_TIME,
            location = "Regina, Saskatchewan",
            locationType = ExperienceLocationType.HYBRID,
            startDate = "2024-01-01",
            endDate = null,
            isCurrent = true,
            summary = "Software development and technology education.",
            companyWebsite = "https://example.com",
            companyLogoUrl = null,
            sortOrder = 1,
            isFeatured = true,
            responsibilities =
                "Develop and maintain software applications.",
            achievements =
                "Delivered multiple production applications.",
        )
    }

    private class FakePortfolioRepository : PortfolioRepository {

        var experiencePage = ExperiencePage(
            items = emptyList(),
            page = 1,
            pageSize = 20,
            totalItems = 0,
            totalPages = 0,
            hasNextPage = false,
            hasPreviousPage = false,
        )

        var error: Throwable? = null

        override suspend fun getExperiences(
            page: Int,
            pageSize: Int,
            search: String?,
            employmentType: String?,
            locationType: String?,
            isCurrent: Boolean?,
            isFeatured: Boolean?,
        ): ExperiencePage {
            error?.let { throw it }

            return experiencePage
        }

        override suspend fun getFeaturedExperiences(
            limit: Int,
        ): List<Experience> {
            return emptyList()
        }

        override suspend fun getExperience(
            slug: String,
        ): Experience {
            return experiencePage.items.first()
        }

        override suspend fun getCategories(): List<ProjectCategory> {
            return emptyList()
        }

        override suspend fun getCategory(
            slug: String,
        ): ProjectCategory {
            error("Not required for ExperienceViewModelTest.")
        }

        override suspend fun getTechnologies(
            category: String?,
        ): List<ProjectTechnology> {
            return emptyList()
        }

        override suspend fun getTechnology(
            slug: String,
        ): ProjectTechnology {
            error("Not required for ExperienceViewModelTest.")
        }

        override suspend fun getProjects(
            page: Int,
            pageSize: Int,
            search: String?,
            categorySlug: String?,
            technologySlug: String?,
            isFeatured: Boolean?,
        ): ProjectPage {
            error("Not required for ExperienceViewModelTest.")
        }

        override suspend fun getFeaturedProjects(
            limit: Int,
        ): List<Project> {
            return emptyList()
        }

        override suspend fun getProject(
            slug: String,
        ): Project {
            error("Not required for ExperienceViewModelTest.")
        }
    }
}