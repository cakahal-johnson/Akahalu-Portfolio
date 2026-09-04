package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectDto(
    val id: String,
    val title: String,
    val slug: String,
    val short_description: String,
    val status: String,
    val visibility: String,
    val is_featured: Boolean,
    val sort_order: Int,
    val thumbnail_url: String? = null,
    val started_at: String? = null,
    val completed_at: String? = null,
    val published_at: String? = null,
    val category: ProjectCategoryDto? = null,
    val technologies: List<ProjectTechnologyDto> = emptyList(),
    val description: String? = null,
    val problem_statement: String? = null,
    val solution_summary: String? = null,
    val key_features: String? = null,
    val technical_highlights: String? = null,
    val repository_url: String? = null,
    val live_url: String? = null,
    val case_study_url: String? = null,
    val seo_title: String? = null,
    val seo_description: String? = null,
    val media: List<ProjectMediaDto> = emptyList(),
    val links: List<ProjectLinkDto> = emptyList(),
)