package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.core.network.ApiClient
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus
import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class ProfileRepositoryImplTest {

    @Test
    fun getProfileCallsPublicProfileEndpointAndMapsResponse() = runTest {
        var requestedPath: String? = null

        val engine = MockEngine { request ->
            requestedPath = request.url.encodedPath

            respond(
                content = profileJson,
                status = HttpStatusCode.OK,
                headers = headersOf(
                    HttpHeaders.ContentType,
                    ContentType.Application.Json.toString(),
                ),
            )
        }

        val client = HttpClient(engine)
        val apiClient = ApiClient(client)
        val remoteDataSource = PortfolioRemoteDataSource(apiClient)
        val repository = PortfolioRepositoryImpl(remoteDataSource)

        val profile = repository.getProfile()

        assertEquals(
            "/portfolio/profile",
            requestedPath,
        )
        assertEquals(
            "Akahalu Vitalis",
            profile.displayName,
        )
        assertEquals(
            "Full-Stack Software Developer",
            profile.professionalTitle,
        )
        assertEquals(
            ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES,
            profile.availabilityStatus,
        )
        assertEquals(
            "Regina, Saskatchewan",
            profile.location,
        )
        assertEquals(
            "Canada",
            profile.country,
        )
        assertEquals(
            "contact@example.com",
            profile.primaryEmail,
        )
        assertEquals(
            true,
            profile.isPublic,
        )

        client.close()
    }

    private companion object {
        const val profileJson = """
            {
              "first_name": "Akahalu",
              "middle_name": "Chinonso",
              "last_name": "Vitalis",
              "display_name": "Akahalu Vitalis",
              "professional_title": "Full-Stack Software Developer",
              "headline": "Building secure, scalable applications.",
              "short_bio": "Software developer focused on modern applications.",
              "biography": "A professional software developer building secure applications.",
              "location": "Regina, Saskatchewan",
              "country": "Canada",
              "timezone": "America/Regina",
              "primary_email": "contact@example.com",
              "phone": "+1 306 555 0100",
              "website_url": "https://example.com",
              "resume_url": "https://example.com/resume.pdf",
              "profile_image_url": "https://example.com/profile.jpg",
              "years_of_experience": 6,
              "availability_status": "open_to_opportunities",
              "availability_message": "Open to opportunities.",
              "is_public": true,
              "seo_title": "Akahalu Vitalis",
              "seo_description": "Full-stack software developer."
            }
        """
    }
}
