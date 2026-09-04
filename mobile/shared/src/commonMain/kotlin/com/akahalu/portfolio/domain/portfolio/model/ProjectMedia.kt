package com.akahalu.portfolio.domain.portfolio.model

enum class ProjectMediaType {
    IMAGE,
    VIDEO,
    DOCUMENT,
    DEMO,
    OTHER,
}

data class ProjectMedia(
    val id: String,
    val projectId: String,
    val mediaType: ProjectMediaType,
    val url: String,
    val thumbnailUrl: String?,
    val altText: String?,
    val caption: String?,
    val provider: String?,
    val providerAssetId: String?,
    val mimeType: String?,
    val width: Int?,
    val height: Int?,
    val fileSizeBytes: Long?,
    val durationSeconds: Int?,
    val isPrimary: Boolean,
    val sortOrder: Int,
)