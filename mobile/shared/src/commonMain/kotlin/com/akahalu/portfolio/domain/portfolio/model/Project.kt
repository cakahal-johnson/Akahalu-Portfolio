package com.akahalu.portfolio.domain.portfolio.model

enum class ProjectStatus {
    DRAFT,
    PUBLISHED,
    ARCHIVED,
}

enum class ProjectVisibility {
    PUBLIC,
    PRIVATE,
    UNLISTED,
}

data class Project(
    val id: String,
    val title: String,
    val slug: String,
    val shortDescription: String,
    val status: ProjectStatus,
    val visibility: ProjectVisibility,
    val isFeatured: Boolean,
    val sortOrder: Int,
    val thumbnailUrl: String?,
    val startedAt: String?,
    val completedAt: String?,
    val publishedAt: String?,
    val category: ProjectCategory?,
    val technologies: List<ProjectTechnology>,
    val description: String?,
    val problemStatement: String?,
    val solutionSummary: String?,
    val keyFeatures: String?,
    val technicalHighlights: String?,
    val repositoryUrl: String?,
    val liveUrl: String?,
    val caseStudyUrl: String?,
    val seoTitle: String?,
    val seoDescription: String?,
    val media: List<ProjectMedia>,
    val links: List<ProjectLink>,
)