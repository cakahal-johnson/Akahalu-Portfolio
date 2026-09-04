package com.akahalu.portfolio.domain.portfolio.model

data class ProjectCategory(
    val id: String,
    val name: String,
    val slug: String,
    val description: String?,
    val icon: String?,
    val color: String?,
    val sortOrder: Int,
    val seoTitle: String?,
    val seoDescription: String?,
)