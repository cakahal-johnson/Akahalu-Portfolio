package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectMediaDto(
    val id: String,
    val project_id: String,
    val media_type: String,
    val url: String,
    val thumbnail_url: String? = null,
    val alt_text: String? = null,
    val caption: String? = null,
    val provider: String? = null,
    val provider_asset_id: String? = null,
    val mime_type: String? = null,
    val width: Int? = null,
    val height: Int? = null,
    val file_size_bytes: Long? = null,
    val duration_seconds: Int? = null,
    val is_primary: Boolean,
    val sort_order: Int,
)