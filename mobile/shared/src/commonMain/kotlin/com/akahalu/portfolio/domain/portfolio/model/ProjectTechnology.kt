package com.akahalu.portfolio.domain.portfolio.model

enum class ProjectTechnologyCategory {
    LANGUAGE,
    FRAMEWORK,
    LIBRARY,
    DATABASE,
    PLATFORM,
    CLOUD,
    DEVOPS,
    TESTING,
    TOOL,
    SERVICE,
    OTHER,
}

data class ProjectTechnology(
    val id: String,
    val name: String,
    val slug: String,
    val category: ProjectTechnologyCategory,
    val icon: String?,
    val officialUrl: String?,
    val color: String?,
    val sortOrder: Int,
    val description: String?,
)