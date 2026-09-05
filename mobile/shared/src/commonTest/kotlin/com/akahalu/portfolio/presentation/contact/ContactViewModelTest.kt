@file:OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)

package com.akahalu.portfolio.presentation.contact

import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

class ContactViewModelTest {

    private val dispatcher = StandardTestDispatcher()

    @BeforeTest
    fun setUp() {
        Dispatchers.setMain(dispatcher)
    }

    @AfterTest
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun initialStateIsLoading() = runTest {
        val repository = FakePortfolioRepository()
        val viewModel = ContactViewModel(
            repository = repository,
            scope = backgroundScope,
        )

        assertIs<ContactUiState.Loading>(
            viewModel.uiState.value,
        )
    }

    @Test
    fun successfulLoadProducesSuccessState() = runTest {
        val expectedProfile = createProfile()

        val repository = FakePortfolioRepository(
            profile = expectedProfile,
        )

        val viewModel = ContactViewModel(
            repository = repository,
            scope = backgroundScope,
        )

        viewModel.loadProfile()
        advanceUntilIdle()

        val state = assertIs<ContactUiState.Success>(
            viewModel.uiState.value,
        )

        assertEquals(
            expectedProfile,
            state.profile,
        )
    }

    @Test
    fun failedLoadProducesErrorState() = runTest {
        val repository = FakePortfolioRepository(
            failure = IllegalStateException("Profile unavailable."),
        )

        val viewModel = ContactViewModel(
            repository = repository,
            scope = backgroundScope,
        )

        viewModel.loadProfile()
        advanceUntilIdle()

        val state = assertIs<ContactUiState.Error>(
            viewModel.uiState.value,
        )

        assertEquals(
            "Profile unavailable.",
            state.message,
        )
    }

    private fun createProfile(): Profile {
        return Profile(
            firstName = "Akahalu",
            middleName = "Chinonso",
            lastName = "Vitalis",
            displayName = "Akahalu Vitalis",
            professionalTitle = "Full-Stack Software Developer",
            headline = "Building secure, scalable applications.",
            shortBio = "Software developer focused on modern applications.",
            biography = "A professional software developer building secure applications.",
            location = "Regina, Saskatchewan",
            country = "Canada",
            timezone = "America/Regina",
            primaryEmail = "contact@example.com",
            phone = "+1 306 555 0100",
            websiteUrl = "https://example.com",
            resumeUrl = "https://example.com/resume.pdf",
            profileImageUrl = "https://example.com/profile.jpg",
            yearsOfExperience = 6,
            availabilityStatus =
                ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES,
            availabilityMessage = "Open to opportunities.",
            isPublic = true,
            seoTitle = "Akahalu Vitalis",
            seoDescription = "Full-stack software developer.",
        )
    }

    private class FakePortfolioRepository(
        private val profile: Profile? = null,
        private val failure: Throwable? = null,
    ) : PortfolioRepository {

        override suspend fun getCategories(): List<ProjectCategory> {
            return emptyList()
        }

        override suspend fun getCategory(
            slug: String,
        ): ProjectCategory {
            error("Not used in this test.")
        }

        override suspend fun getTechnologies(
            category: String?,
        ): List<ProjectTechnology> {
            return emptyList()
        }

        override suspend fun getTechnology(
            slug: String,
        ): ProjectTechnology {
            error("Not used in this test.")
        }

        override suspend fun getProjects(
            page: Int,
            pageSize: Int,
            search: String?,
            categorySlug: String?,
            technologySlug: String?,
            isFeatured: Boolean?,
        ): ProjectPage {
            error("Not used in this test.")
        }

        override suspend fun getFeaturedProjects(
            limit: Int,
        ): List<Project> {
            return emptyList()
        }

        override suspend fun getProject(
            slug: String,
        ): Project {
            error("Not used in this test.")
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
            error("Not used in this test.")
        }

        override suspend fun getFeaturedExperiences(
            limit: Int,
        ): List<Experience> {
            return emptyList()
        }

        override suspend fun getExperience(
            slug: String,
        ): Experience {
            error("Not used in this test.")
        }

        override suspend fun getProfile(): Profile {
            failure?.let { throw it }

            return requireNotNull(profile)
        }
    }
}
