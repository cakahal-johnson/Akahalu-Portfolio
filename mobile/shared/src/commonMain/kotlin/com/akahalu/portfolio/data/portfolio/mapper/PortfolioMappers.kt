package com.akahalu.portfolio.data.portfolio.mapper

import com.akahalu.portfolio.data.portfolio.dto.ProjectCategoryDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectLinkDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectListResponseDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectMediaDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectSummaryDto
import com.akahalu.portfolio.data.portfolio.dto.ProjectTechnologyDto
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectLink
import com.akahalu.portfolio.domain.portfolio.model.ProjectLinkType
import com.akahalu.portfolio.domain.portfolio.model.ProjectMedia
import com.akahalu.portfolio.domain.portfolio.model.ProjectMediaType
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnologyCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectVisibility
import com.akahalu.portfolio.data.portfolio.dto.ExperienceDto
import com.akahalu.portfolio.data.portfolio.dto.ExperienceListResponseDto
import com.akahalu.portfolio.data.portfolio.dto.ExperienceSummaryDto
import com.akahalu.portfolio.domain.portfolio.model.EmploymentType
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperienceLocationType
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage

fun ProjectCategoryDto.toDomain(): ProjectCategory {
    return ProjectCategory(
        id = id,
        name = name,
        slug = slug,
        description = description,
        icon = icon,
        color = color,
        sortOrder = sort_order,
        seoTitle = seo_title,
        seoDescription = seo_description,
    )
}

fun ProjectTechnologyDto.toDomain(): ProjectTechnology {
    return ProjectTechnology(
        id = id,
        name = name,
        slug = slug,
        category = category.toProjectTechnologyCategory(),
        icon = icon,
        officialUrl = official_url,
        color = color,
        sortOrder = sort_order,
        description = description,
    )
}

fun ProjectMediaDto.toDomain(): ProjectMedia {
    return ProjectMedia(
        id = id,
        projectId = project_id,
        mediaType = media_type.toProjectMediaType(),
        url = url,
        thumbnailUrl = thumbnail_url,
        altText = alt_text,
        caption = caption,
        provider = provider,
        providerAssetId = provider_asset_id,
        mimeType = mime_type,
        width = width,
        height = height,
        fileSizeBytes = file_size_bytes,
        durationSeconds = duration_seconds,
        isPrimary = is_primary,
        sortOrder = sort_order,
    )
}

fun ProjectLinkDto.toDomain(): ProjectLink {
    return ProjectLink(
        id = id,
        projectId = project_id,
        label = label,
        url = url,
        linkType = link_type.toProjectLinkType(),
        icon = icon,
        opensInNewTab = opens_in_new_tab,
        sortOrder = sort_order,
    )
}

fun ProjectSummaryDto.toDomain(): Project {
    return Project(
        id = id,
        title = title,
        slug = slug,
        shortDescription = short_description,
        status = status.toProjectStatus(),
        visibility = visibility.toProjectVisibility(),
        isFeatured = is_featured,
        sortOrder = sort_order,
        thumbnailUrl = thumbnail_url,
        startedAt = started_at,
        completedAt = completed_at,
        publishedAt = published_at,
        category = category?.toDomain(),
        technologies = technologies.map(ProjectTechnologyDto::toDomain),
        description = null,
        problemStatement = null,
        solutionSummary = null,
        keyFeatures = null,
        technicalHighlights = null,
        repositoryUrl = null,
        liveUrl = null,
        caseStudyUrl = null,
        seoTitle = null,
        seoDescription = null,
        media = emptyList(),
        links = emptyList(),
    )
}

fun ProjectDto.toDomain(): Project {
    return Project(
        id = id,
        title = title,
        slug = slug,
        shortDescription = short_description,
        status = status.toProjectStatus(),
        visibility = visibility.toProjectVisibility(),
        isFeatured = is_featured,
        sortOrder = sort_order,
        thumbnailUrl = thumbnail_url,
        startedAt = started_at,
        completedAt = completed_at,
        publishedAt = published_at,
        category = category?.toDomain(),
        technologies = technologies.map(ProjectTechnologyDto::toDomain),
        description = description,
        problemStatement = problem_statement,
        solutionSummary = solution_summary,
        keyFeatures = key_features,
        technicalHighlights = technical_highlights,
        repositoryUrl = repository_url,
        liveUrl = live_url,
        caseStudyUrl = case_study_url,
        seoTitle = seo_title,
        seoDescription = seo_description,
        media = media.map(ProjectMediaDto::toDomain),
        links = links.map(ProjectLinkDto::toDomain),
    )
}

fun ProjectListResponseDto.toDomain(): ProjectPage {
    return ProjectPage(
        items = items.map(ProjectSummaryDto::toDomain),
        page = page,
        pageSize = page_size,
        totalItems = total_items,
        totalPages = total_pages,
        hasNextPage = has_next_page,
        hasPreviousPage = has_previous_page,
    )
}

private fun String.toProjectTechnologyCategory(): ProjectTechnologyCategory {
    return when (lowercase()) {
        "language" -> ProjectTechnologyCategory.LANGUAGE
        "framework" -> ProjectTechnologyCategory.FRAMEWORK
        "library" -> ProjectTechnologyCategory.LIBRARY
        "database" -> ProjectTechnologyCategory.DATABASE
        "platform" -> ProjectTechnologyCategory.PLATFORM
        "cloud" -> ProjectTechnologyCategory.CLOUD
        "devops" -> ProjectTechnologyCategory.DEVOPS
        "testing" -> ProjectTechnologyCategory.TESTING
        "tool" -> ProjectTechnologyCategory.TOOL
        "service" -> ProjectTechnologyCategory.SERVICE
        else -> ProjectTechnologyCategory.OTHER
    }
}

private fun String.toProjectMediaType(): ProjectMediaType {
    return when (lowercase()) {
        "image" -> ProjectMediaType.IMAGE
        "video" -> ProjectMediaType.VIDEO
        "document" -> ProjectMediaType.DOCUMENT
        "demo" -> ProjectMediaType.DEMO
        else -> ProjectMediaType.OTHER
    }
}

private fun String.toProjectLinkType(): ProjectLinkType {
    return when (lowercase()) {
        "repository" -> ProjectLinkType.REPOSITORY
        "live_demo" -> ProjectLinkType.LIVE_DEMO
        "documentation" -> ProjectLinkType.DOCUMENTATION
        "case_study" -> ProjectLinkType.CASE_STUDY
        "video" -> ProjectLinkType.VIDEO
        "download" -> ProjectLinkType.DOWNLOAD
        "app_store" -> ProjectLinkType.APP_STORE
        "play_store" -> ProjectLinkType.PLAY_STORE
        "design" -> ProjectLinkType.DESIGN
        "article" -> ProjectLinkType.ARTICLE
        "api" -> ProjectLinkType.API
        else -> ProjectLinkType.OTHER
    }
}

private fun String.toProjectStatus(): ProjectStatus {
    return when (lowercase()) {
        "published" -> ProjectStatus.PUBLISHED
        "archived" -> ProjectStatus.ARCHIVED
        else -> ProjectStatus.DRAFT
    }
}

private fun String.toProjectVisibility(): ProjectVisibility {
    return when (lowercase()) {
        "public" -> ProjectVisibility.PUBLIC
        "unlisted" -> ProjectVisibility.UNLISTED
        else -> ProjectVisibility.PRIVATE
    }
}

fun ExperienceSummaryDto.toDomain(): Experience {
    return Experience(
        id = id,
        companyName = company_name,
        jobTitle = job_title,
        slug = slug,
        employmentType = employment_type.toEmploymentType(),
        location = location,
        locationType = location_type.toExperienceLocationType(),
        startDate = start_date,
        endDate = end_date,
        isCurrent = is_current,
        summary = summary,
        companyWebsite = company_website,
        companyLogoUrl = company_logo_url,
        sortOrder = sort_order,
        isFeatured = is_featured,
        responsibilities = null,
        achievements = null,
    )
}

fun ExperienceDto.toDomain(): Experience {
    return Experience(
        id = id,
        companyName = company_name,
        jobTitle = job_title,
        slug = slug,
        employmentType = employment_type.toEmploymentType(),
        location = location,
        locationType = location_type.toExperienceLocationType(),
        startDate = start_date,
        endDate = end_date,
        isCurrent = is_current,
        summary = summary,
        companyWebsite = company_website,
        companyLogoUrl = company_logo_url,
        sortOrder = sort_order,
        isFeatured = is_featured,
        responsibilities = responsibilities,
        achievements = achievements,
    )
}

fun ExperienceListResponseDto.toDomain(): ExperiencePage {
    return ExperiencePage(
        items = items.map(
            ExperienceSummaryDto::toDomain,
        ),
        page = page,
        pageSize = page_size,
        totalItems = total_items,
        totalPages = total_pages,
        hasNextPage = has_next_page,
        hasPreviousPage = has_previous_page,
    )
}

private fun String.toEmploymentType(): EmploymentType {
    return when (lowercase()) {
        "full_time" -> EmploymentType.FULL_TIME
        "part_time" -> EmploymentType.PART_TIME
        "contract" -> EmploymentType.CONTRACT
        "freelance" -> EmploymentType.FREELANCE
        "internship" -> EmploymentType.INTERNSHIP
        "apprenticeship" -> EmploymentType.APPRENTICESHIP
        "temporary" -> EmploymentType.TEMPORARY
        "volunteer" -> EmploymentType.VOLUNTEER
        "self_employed" -> EmploymentType.SELF_EMPLOYED
        else -> EmploymentType.OTHER
    }
}

private fun String.toExperienceLocationType(): ExperienceLocationType {
    return when (lowercase()) {
        "onsite" -> ExperienceLocationType.ONSITE
        "remote" -> ExperienceLocationType.REMOTE
        "hybrid" -> ExperienceLocationType.HYBRID
        else -> ExperienceLocationType.ONSITE
    }
}