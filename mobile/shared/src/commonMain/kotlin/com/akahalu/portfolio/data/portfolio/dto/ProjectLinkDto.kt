package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProjectLinkDto(
    val id: String,
    val project_id: String,
    val label: String,
    val url: String,
    val link_type: String,
    val icon: String? = null,
    val opens_in_new_tab: Boolean,
    val sort_order: Int,
)