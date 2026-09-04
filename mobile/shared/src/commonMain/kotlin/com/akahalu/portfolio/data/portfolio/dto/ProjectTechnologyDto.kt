package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectTechnologyDto(
    val id: String,
    val name: String,
    val slug: String,
    val category: String,
    val icon: String? = null,
    val official_url: String? = null,
    val color: String? = null,
    val sort_order: Int,
    val description: String? = null,
)