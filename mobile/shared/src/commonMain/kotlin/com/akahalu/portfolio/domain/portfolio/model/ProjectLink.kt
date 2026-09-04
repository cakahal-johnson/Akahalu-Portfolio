package com.akahalu.portfolio.domain.portfolio.model

enum class ProjectLinkType {
    REPOSITORY,
    LIVE_DEMO,
    DOCUMENTATION,
    CASE_STUDY,
    VIDEO,
    DOWNLOAD,
    APP_STORE,
    PLAY_STORE,
    DESIGN,
    ARTICLE,
    API,
    OTHER,
}

data class ProjectLink(
    val id: String,
    val projectId: String,
    val label: String,
    val url: String,
    val linkType: ProjectLinkType,
    val icon: String?,
    val opensInNewTab: Boolean,
    val sortOrder: Int,
)