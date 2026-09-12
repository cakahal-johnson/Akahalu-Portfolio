package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.data.portfolio.cache.JsonPortfolioCache
import com.akahalu.portfolio.data.portfolio.dto.ExperienceListResponseDto
import com.akahalu.portfolio.data.portfolio.dto.ProfileDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectListResponseDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectSummaryDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectTechnologyDto
import com.akahalu.portfolio.data.portfolio.mapper.toDomain
import com.akahalu.portfolio.data.portfolio.mapper.toDto
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmission
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmissionResult
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
    private val cache: JsonPortfolioCache,
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
        val cacheKey = technologiesCacheKey(category)

        return runCatching {
            val remoteData = remoteDataSource
                .getTechnologies(category)

            cache.save(
                key = cacheKey,
                value = remoteData,
                serializer = kotlinx.serialization.builtins.ListSerializer(
                    ProjectTechnologyDto.serializer(),
                ),
            )

            remoteData.map { it.toDomain() }
        }.getOrElse { exception ->
            cache.get(
                key = cacheKey,
                serializer = kotlinx.serialization.builtins.ListSerializer(
                    ProjectTechnologyDto.serializer(),
                ),
            )?.map { it.toDomain() }
                ?: throw exception
        }
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
        val cacheKey = projectsCacheKey(
            page = page,
            pageSize = pageSize,
            search = search,
            categorySlug = categorySlug,
            technologySlug = technologySlug,
            isFeatured = isFeatured,
        )

        return runCatching {
            val remoteData = remoteDataSource.getProjects(
                page = page,
                pageSize = pageSize,
                search = search,
                categorySlug = categorySlug,
                technologySlug = technologySlug,
                isFeatured = isFeatured,
            )

            cache.save(
                key = cacheKey,
                value = remoteData,
                serializer = ProjectListResponseDto.serializer(),
            )

            remoteData.toDomain()
        }.getOrElse { exception ->
            cache.get(
                key = cacheKey,
                serializer = ProjectListResponseDto.serializer(),
            )?.toDomain()
                ?: throw exception
        }
    }

    override suspend fun getFeaturedProjects(
        limit: Int,
    ): List<Project> {
        val cacheKey = "featured_projects_$limit"

        return runCatching {
            val remoteData = remoteDataSource
                .getFeaturedProjects(limit)

            cache.save(
                key = cacheKey,
                value = remoteData,
                serializer = kotlinx.serialization.builtins.ListSerializer(
                    ProjectSummaryDto.serializer(),
                ),
            )

            remoteData.map { it.toDomain() }
        }.getOrElse { exception ->
            cache.get(
                key = cacheKey,
                serializer = kotlinx.serialization.builtins.ListSerializer(
                    ProjectSummaryDto.serializer(),
                ),
            )?.map { it.toDomain() }
                ?: throw exception
        }
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
        val cacheKey = experiencesCacheKey(
            page = page,
            pageSize = pageSize,
            search = search,
            employmentType = employmentType,
            locationType = locationType,
            isCurrent = isCurrent,
            isFeatured = isFeatured,
        )

        return runCatching {
            val remoteData = remoteDataSource.getExperiences(
                page = page,
                pageSize = pageSize,
                search = search,
                employmentType = employmentType,
                locationType = locationType,
                isCurrent = isCurrent,
                isFeatured = isFeatured,
            )

            cache.save(
                key = cacheKey,
                value = remoteData,
                serializer = ExperienceListResponseDto.serializer(),
            )

            remoteData.toDomain()
        }.getOrElse { exception ->
            cache.get(
                key = cacheKey,
                serializer = ExperienceListResponseDto.serializer(),
            )?.toDomain()
                ?: throw exception
        }
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
        val cacheKey = "profile"

        return runCatching {
            val remoteData = remoteDataSource.getProfile()

            cache.save(
                key = cacheKey,
                value = remoteData,
                serializer = ProfileDto.serializer(),
            )

            remoteData.toDomain()
        }.getOrElse { exception ->
            cache.get(
                key = cacheKey,
                serializer = ProfileDto.serializer(),
            )?.toDomain()
                ?: throw exception
        }
    }

    override suspend fun submitContactInquiry(
        submission: ContactInquirySubmission,
    ): ContactInquirySubmissionResult {
        return remoteDataSource
            .submitContactInquiry(
                submission.toDto(),
            )
            .toDomain()
    }

    private fun technologiesCacheKey(
        category: String?,
    ): String {
        return "technologies_${category ?: "all"}"
    }

    private fun projectsCacheKey(
        page: Int,
        pageSize: Int,
        search: String?,
        categorySlug: String?,
        technologySlug: String?,
        isFeatured: Boolean?,
    ): String {
        return listOf(
            "projects",
            page,
            pageSize,
            search ?: "",
            categorySlug ?: "",
            technologySlug ?: "",
            isFeatured?.toString() ?: "",
        ).joinToString("_")
    }

    private fun experiencesCacheKey(
        page: Int,
        pageSize: Int,
        search: String?,
        employmentType: String?,
        locationType: String?,
        isCurrent: Boolean?,
        isFeatured: Boolean?,
    ): String {
        return listOf(
            "experiences",
            page,
            pageSize,
            search ?: "",
            employmentType ?: "",
            locationType ?: "",
            isCurrent?.toString() ?: "",
            isFeatured?.toString() ?: "",
        ).joinToString("_")
    }
}