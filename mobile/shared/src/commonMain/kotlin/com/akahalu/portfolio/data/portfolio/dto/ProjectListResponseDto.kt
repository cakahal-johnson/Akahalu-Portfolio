package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectListResponseDto(
    val items: List<ProjectSummaryDto> = emptyList(),
    val page: Int,
    val page_size: Int,
    val total_items: Int,
    val total_pages: Int,
    val has_next_page: Boolean,
    val has_previous_page: Boolean,
)