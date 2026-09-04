package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.core.network.ApiClient
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnologyCategory
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

class PortfolioRepositoryImplTest {

    private fun createRepository(
        response: String,
    ): PortfolioRepositoryImpl {
        val engine = MockEngine(
            MockEngineConfig().apply {
                requestHandlers.add {
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

        val apiClient = ApiClient(httpClient)

        return PortfolioRepositoryImpl(
            PortfolioRemoteDataSource(apiClient),
        )
    }

    @Test
    fun getCategoriesMapsRemoteResponse() = runTest {
        val repository = createRepository(
            response = """
                [
                    {
                        "id": "category-1",
                        "name": "Web Development",
                        "slug": "web-development",
                        "description": "Web projects",
                        "icon": "code",
                        "color": "#2563EB",
                        "sort_order": 1,
                        "seo_title": "Web Development",
                        "seo_description": "Web projects"
                    }
                ]
            """.trimIndent(),
        )

        val result = repository.getCategories()

        assertEquals(
            1,
            result.size,
        )
        assertEquals(
            "web-development",
            result.first().slug,
        )
    }

    @Test
    fun getTechnologiesMapsCategory() = runTest {
        val repository = createRepository(
            response = """
                [
                    {
                        "id": "technology-1",
                        "name": "FastAPI",
                        "slug": "fastapi",
                        "category": "framework",
                        "icon": "fastapi",
                        "official_url": "https://fastapi.tiangolo.com",
                        "color": "#009688",
                        "sort_order": 1,
                        "description": "Python API framework"
                    }
                ]
            """.trimIndent(),
        )

        val result = repository.getTechnologies()

        assertEquals(
            1,
            result.size,
        )
        assertEquals(
            ProjectTechnologyCategory.FRAMEWORK,
            result.first().category,
        )
    }

    @Test
    fun getProjectsMapsPagination() = runTest {
        val repository = createRepository(
            response = """
                {
                    "items": [
                        {
                            "id": "project-1",
                            "title": "Akahalu Portfolio",
                            "slug": "akahalu-portfolio",
                            "short_description": "Production-ready portfolio",
                            "status": "published",
                            "visibility": "public",
                            "is_featured": true,
                            "sort_order": 1,
                            "thumbnail_url": "https://example.com/image.webp",
                            "started_at": null,
                            "completed_at": null,
                            "published_at": "2026-09-01T00:00:00Z",
                            "category": null,
                            "technologies": []
                        }
                    ],
                    "page": 1,
                    "page_size": 20,
                    "total_items": 1,
                    "total_pages": 1,
                    "has_next_page": false,
                    "has_previous_page": false
                }
            """.trimIndent(),
        )

        val result = repository.getProjects()

        assertEquals(
            1,
            result.items.size,
        )
        assertEquals(
            1,
            result.totalItems,
        )
        assertEquals(
            1,
            result.totalPages,
        )
        assertTrue(
            result.items.first().isFeatured,
        )
        assertEquals(
            ProjectStatus.PUBLISHED,
            result.items.first().status,
        )
    }

    @Test
    fun getProjectMapsDetailedResponse() = runTest {
        val repository = createRepository(
            response = """
                {
                    "id": "project-1",
                    "title": "Akahalu Portfolio",
                    "slug": "akahalu-portfolio",
                    "short_description": "Production-ready portfolio",
                    "status": "published",
                    "visibility": "public",
                    "is_featured": true,
                    "sort_order": 1,
                    "thumbnail_url": null,
                    "started_at": null,
                    "completed_at": null,
                    "published_at": "2026-09-01T00:00:00Z",
                    "category": null,
                    "technologies": [],
                    "description": "Full-stack portfolio platform.",
                    "problem_statement": "Present professional work.",
                    "solution_summary": "A modern portfolio platform.",
                    "key_features": "Projects, experience and contact.",
                    "technical_highlights": "KMP, Compose and FastAPI.",
                    "repository_url": "https://github.com/example/project",
                    "live_url": "https://example.com",
                    "case_study_url": null,
                    "seo_title": "Akahalu Portfolio",
                    "seo_description": "Professional portfolio.",
                    "media": [],
                    "links": []
                }
            """.trimIndent(),
        )

        val result = repository.getProject(
            "akahalu-portfolio",
        )

        assertEquals(
            "akahalu-portfolio",
            result.slug,
        )
        assertEquals(
            "Full-stack portfolio platform.",
            result.description,
        )
        assertEquals(
            "https://example.com",
            result.liveUrl,
        )
        assertTrue(
            result.isFeatured,
        )
    }

    @Test
    fun getFeaturedProjectsMapsSummaryResponse() = runTest {
        val repository = createRepository(
            response = """
                [
                    {
                        "id": "project-1",
                        "title": "Featured Project",
                        "slug": "featured-project",
                        "short_description": "Featured portfolio project",
                        "status": "published",
                        "visibility": "public",
                        "is_featured": true,
                        "sort_order": 1,
                        "thumbnail_url": null,
                        "started_at": null,
                        "completed_at": null,
                        "published_at": "2026-09-01T00:00:00Z",
                        "category": null,
                        "technologies": []
                    }
                ]
            """.trimIndent(),
        )

        val result = repository.getFeaturedProjects()

        assertEquals(
            1,
            result.size,
        )
        assertEquals(
            "featured-project",
            result.first().slug,
        )
        assertTrue(
            result.first().isFeatured,
        )
    }
}