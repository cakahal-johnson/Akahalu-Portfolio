package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.data.portfolio.mapper.toDomain
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository

class PortfolioRepositoryImpl(
    private val remoteDataSource: PortfolioRemoteDataSource,
) : PortfolioRepository {

    override suspend fun getCategories(): List<ProjectCategory> {
        return remoteDataSource
            .getCategories()
            .map { it.toDomain() }
    }

    override suspend fun getCategory(
        slug: String,
    ): ProjectCategory {
        return remoteDataSource
            .getCategory(slug)
            .toDomain()
    }

    override suspend fun getTechnologies(
        category: String?,
    ): List<ProjectTechnology> {
        return remoteDataSource
            .getTechnologies(category)
            .map { it.toDomain() }
    }

    override suspend fun getTechnology(
        slug: String,
    ): ProjectTechnology {
        return remoteDataSource
            .getTechnology(slug)
            .toDomain()
    }

    override suspend fun getProjects(
        page: Int,
        pageSize: Int,
        search: String?,
        categorySlug: String?,
        technologySlug: String?,
        isFeatured: Boolean?,
    ): ProjectPage {
        return remoteDataSource
            .getProjects(
                page = page,
                pageSize = pageSize,
                search = search,
                categorySlug = categorySlug,
                technologySlug = technologySlug,
                isFeatured = isFeatured,
            )
            .toDomain()
    }

    override suspend fun getFeaturedProjects(
        limit: Int,
    ): List<Project> {
        return remoteDataSource
            .getFeaturedProjects(limit)
            .map { it.toDomain() }
    }

    override suspend fun getProject(
        slug: String,
    ): Project {
        return remoteDataSource
            .getProject(slug)
            .toDomain()
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
        return remoteDataSource
            .getExperiences(
                page = page,
                pageSize = pageSize,
                search = search,
                employmentType = employmentType,
                locationType = locationType,
                isCurrent = isCurrent,
                isFeatured = isFeatured,
            )
            .toDomain()
    }

    override suspend fun getFeaturedExperiences(
        limit: Int,
    ): List<Experience> {
        return remoteDataSource
            .getFeaturedExperiences(limit)
            .map { it.toDomain() }
    }

    override suspend fun getExperience(
        slug: String,
    ): Experience {
        return remoteDataSource
            .getExperience(slug)
            .toDomain()
    }

    override suspend fun getProfile(): Profile {
        return remoteDataSource
            .getProfile()
            .toDomain()
    }
}
