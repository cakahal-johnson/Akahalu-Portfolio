package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.core.network.ApiClient
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.MockEngineConfig
import io.ktor.client.engine.mock.respond
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ExperienceRepositoryImplTest {

    @Test
    fun getExperiences_mapsPaginationAndExperienceFields() =
        runTest {
            val repository = createRepository(
                response = """
                    {
                        "items": [
                            {
                                "id": "experience-1",
                                "company_name": "Akahalu Technologies",
                                "job_title": "Software Developer",
                                "slug": "software-developer",
                                "employment_type": "full_time",
                                "location": "Regina, Saskatchewan",
                                "location_type": "hybrid",
                                "start_date": "2024-01-01",
                                "end_date": null,
                                "is_current": true,
                                "summary": "Software development and technology education.",
                                "company_website": "https://example.com",
                                "company_logo_url": null,
                                "sort_order": 1,
                                "is_featured": true,
                                "responsibilities": "Develop applications.",
                                "achievements": "Delivered production applications."
                            }
                        ],
                        "page": 2,
                        "page_size": 10,
                        "total_items": 21,
                        "total_pages": 3,
                        "has_next_page": true,
                        "has_previous_page": true
                    }
                """.trimIndent(),
            )

            val result = repository.getExperiences(
                page = 2,
                pageSize = 10,
            )

            assertEquals(
                2,
                result.page,
            )
            assertEquals(
                10,
                result.pageSize,
            )
            assertEquals(
                21,
                result.totalItems,
            )
            assertEquals(
                3,
                result.totalPages,
            )
            assertTrue(
                result.hasNextPage,
            )
            assertTrue(
                result.hasPreviousPage,
            )

            val experience = result.items.single()

            assertEquals(
                "experience-1",
                experience.id,
            )
            assertEquals(
                "Akahalu Technologies",
                experience.companyName,
            )
            assertEquals(
                "Software Developer",
                experience.jobTitle,
            )
            assertEquals(
                "software-developer",
                experience.slug,
            )
            assertEquals(
                "Regina, Saskatchewan",
                experience.location,
            )
            assertTrue(
                experience.isCurrent,
            )
            assertTrue(
                experience.isFeatured,
            )
        }

    @Test
    fun getFeaturedExperiences_mapsSummaryResponse() =
        runTest {
            val repository = createRepository(
                response = """
                    [
                        {
                            "id": "experience-1",
                            "company_name": "Akahalu Technologies",
                            "job_title": "Software Developer",
                            "slug": "software-developer",
                            "employment_type": "full_time",
                            "location": "Regina, Saskatchewan",
                            "location_type": "hybrid",
                            "start_date": "2024-01-01",
                            "end_date": null,
                            "is_current": true,
                            "summary": "Software development and technology education.",
                            "company_website": "https://example.com",
                            "company_logo_url": null,
                            "sort_order": 1,
                            "is_featured": true
                        }
                    ]
                """.trimIndent(),
            )

            val result = repository.getFeaturedExperiences(
                limit = 3,
            )

            assertEquals(
                1,
                result.size,
            )

            val experience = result.single()

            assertEquals(
                "experience-1",
                experience.id,
            )
            assertEquals(
                "software-developer",
                experience.slug,
            )
            assertEquals(
                "Akahalu Technologies",
                experience.companyName,
            )
            assertTrue(
                experience.isFeatured,
            )
        }

    @Test
    fun getExperience_mapsDetailedResponse() =
        runTest {
            val repository = createRepository(
                response = """
                    {
                        "id": "experience-1",
                        "company_name": "Akahalu Technologies",
                        "job_title": "Software Developer",
                        "slug": "software-developer",
                        "employment_type": "full_time",
                        "location": "Regina, Saskatchewan",
                        "location_type": "hybrid",
                        "start_date": "2024-01-01",
                        "end_date": null,
                        "is_current": true,
                        "summary": "Software development and technology education.",
                        "company_website": "https://example.com",
                        "company_logo_url": null,
                        "sort_order": 1,
                        "is_featured": true,
                        "responsibilities": "Develop and maintain software applications.",
                        "achievements": "Delivered multiple production applications."
                    }
                """.trimIndent(),
            )

            val result = repository.getExperience(
                slug = "software-developer",
            )

            assertEquals(
                "software-developer",
                result.slug,
            )
            assertEquals(
                "Develop and maintain software applications.",
                result.responsibilities,
            )
            assertEquals(
                "Delivered multiple production applications.",
                result.achievements,
            )
            assertEquals(
                "https://example.com",
                result.companyWebsite,
            )
            assertTrue(
                result.isCurrent,
            )
        }

    @Test
    fun getExperiences_sendsSupportedQueryParameters() =
        runTest {
            var capturedParameters: Map<String, String?> =
                emptyMap()

            val repository = createRepository(
                response = """
                    {
                        "items": [],
                        "page": 2,
                        "page_size": 10,
                        "total_items": 0,
                        "total_pages": 0,
                        "has_next_page": false,
                        "has_previous_page": false
                    }
                """.trimIndent(),
                requestInspector = { request ->
                    capturedParameters = mapOf(
                        "page" to request.url.parameters["page"],
                        "page_size" to
                                request.url.parameters["page_size"],
                        "search" to
                                request.url.parameters["search"],
                        "employment_type" to
                                request.url.parameters["employment_type"],
                        "location_type" to
                                request.url.parameters["location_type"],
                        "is_current" to
                                request.url.parameters["is_current"],
                        "is_featured" to
                                request.url.parameters["is_featured"],
                    )
                },
            )

            repository.getExperiences(
                page = 2,
                pageSize = 10,
                search = "software",
                employmentType = "full_time",
                locationType = "hybrid",
                isCurrent = true,
                isFeatured = false,
            )

            assertEquals(
                "2",
                capturedParameters["page"],
            )
            assertEquals(
                "10",
                capturedParameters["page_size"],
            )
            assertEquals(
                "software",
                capturedParameters["search"],
            )
            assertEquals(
                "full_time",
                capturedParameters["employment_type"],
            )
            assertEquals(
                "hybrid",
                capturedParameters["location_type"],
            )
            assertEquals(
                "true",
                capturedParameters["is_current"],
            )
            assertEquals(
                "false",
                capturedParameters["is_featured"],
            )
        }

    private fun createRepository(
        response: String,
        requestInspector:
            (io.ktor.client.request.HttpRequestData) -> Unit = {},
    ): PortfolioRepositoryImpl {
        val engine = MockEngine(
            MockEngineConfig().apply {
                requestHandlers.add { request ->
                    requestInspector(request)

                    respond(
                        content = response,
                        status = HttpStatusCode.OK,
                        headers = headersOf(
                            "Content-Type",
                            ContentType.Application.Json.toString(),
                        ),
                    )
                }
            },
        )

        val httpClient = HttpClient(engine) {
            install(ContentNegotiation) {
                json(
                    Json {
                        ignoreUnknownKeys = true
                        explicitNulls = false
                    },
                )
            }
        }

        return PortfolioRepositoryImpl(
            remoteDataSource = PortfolioRemoteDataSource(
                apiClient = ApiClient(httpClient),
            ),
        )
    }
}