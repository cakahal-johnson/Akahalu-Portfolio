package com.akahalu.portfolio.data.portfolio.remote

import com.akahalu.portfolio.core.network.ApiClient
import com.akahalu.portfolio.data.portfolio.dto.ProjectCategoryDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectListResponseDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectSummaryDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectTechnologyDto
import io.ktor.client.request.parameter

class PortfolioRemoteDataSource(
    private val apiClient: ApiClient,
) {

    suspend fun getCategories(): List<ProjectCategoryDto> {
        return apiClient.get(
            path = "portfolio/categories",
        )
    }

    suspend fun getCategory(
        slug: String,
    ): ProjectCategoryDto {
        return apiClient.get(
            path = "portfolio/categories/$slug",
        )
    }

    suspend fun getTechnologies(
        category: String? = null,
    ): List<ProjectTechnologyDto> {
        return apiClient.get(
            path = "portfolio/technologies",
        ) {
            category?.let {
                parameter(
                    "category",
                    it,
                )
            }
        }
    }

    suspend fun getTechnology(
        slug: String,
    ): ProjectTechnologyDto {
        return apiClient.get(
            path = "portfolio/technologies/$slug",
        )
    }

    suspend fun getProjects(
        page: Int = 1,
        pageSize: Int = 20,
        search: String? = null,
        categorySlug: String? = null,
        technologySlug: String? = null,
        isFeatured: Boolean? = null,
    ): ProjectListResponseDto {
        return apiClient.get(
            path = "portfolio/projects",
        ) {
            parameter(
                "page",
                page,
            )
            parameter(
                "page_size",
                pageSize,
            )

            search?.let {
                parameter(
                    "search",
                    it,
                )
            }

            categorySlug?.let {
                parameter(
                    "category_slug",
                    it,
                )
            }

            technologySlug?.let {
                parameter(
                    "technology_slug",
                    it,
                )
            }

            isFeatured?.let {
                parameter(
                    "is_featured",
                    it,
                )
            }
        }
    }

    suspend fun getFeaturedProjects(
        limit: Int = 6,
    ): List<ProjectSummaryDto> {
        return apiClient.get(
            path = "portfolio/projects/featured",
        ) {
            parameter(
                "limit",
                limit,
            )
        }
    }

    suspend fun getProject(
        slug: String,
    ): ProjectDto {
        return apiClient.get(
            path = "portfolio/projects/$slug",
        )
    }
}