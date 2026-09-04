package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectSummaryDto(
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
)