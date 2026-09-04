package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectCategoryDto(
    val id: String,
    val name: String,
    val slug: String,
    val description: String? = null,
    val icon: String? = null,
    val color: String? = null,
    val sort_order: Int,
    val seo_title: String? = null,
    val seo_description: String? = null,
)